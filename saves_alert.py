"""
NHL goalie saves prop alerts for DraftKings and FanDuel.

Checks The Odds API for the `player_total_saves` market on upcoming NHL games and
sends a Telegram message whenever a goalie's saves line appears at a book for the
first time. Books often post one goalie early and the other hours later, so each
goalie is tracked separately and games keep being rechecked until both are posted.

How credits are spent (The Odds API free plan = 500 credits/month):
  * Listing games (/events) is free.
  * Both books are checked in one call. A check costs 1 credit only if it returns
    lines; a check on a game with nothing posted yet is free.
  * So games with nothing posted are checked every run for free. Once a game has
    some lines, it's rechecked (1 credit each) every RECHECK_MINUTES, only within
    RECHECK_WINDOW_HOURS of puck drop, until both books show two goalies.
  * Rechecks stop when credits fall to RECHECK_RESERVE, so first-goalie alerts
    keep working for the rest of the month.

Environment variables:
  ODDS_API_KEY          The Odds API key (required)
  TELEGRAM_BOT_TOKEN    Token from @BotFather (required to send alerts)
  TELEGRAM_CHAT_ID      Your chat ID with the bot (required to send alerts)
  TELEGRAM_SILENT       "true" (default) = alerts arrive without sound; "false" = normal
  TEAMS                 Optional comma-separated filter, e.g. "Red Wings,Rangers".
                        Empty = all games.
  BOOKS                 Optional, default "draftkings,fanduel"
  LOOKAHEAD_HOURS       How far ahead to look for games (default 30)
  RECHECK_MINUTES       How often to recheck games that are partly posted (default 60)
  RECHECK_WINDOW_HOURS  Only recheck games starting within this many hours (default 10)
  RECHECK_RESERVE       Stop rechecks when credits fall to this level (default 150)
  MIN_CREDITS           Stop all checks below this many credits (default 20)
  SHOT_THRESHOLD        Only watch games where a goalie's expected shots differ from the
                        league average by at least this much (default 2). 0 = watch every game.
  TARGET_SAVES          Size of the "lean" zone in saves (default 1). See tag_code().
  TEST_PUSH             "true" = send a test notification and exit

Matchup filter (uses this season's NHL team stats, free, refreshed every 6 hours):
  Team shots for/against are opponent-adjusted: each game is rated against what that
  opponent usually allows/shoots (excluding its games vs. this team), so a team that has
  faced weak shooters doesn't look like an elite defense. Home/road splits are blended in.
  expected shots on a goalie = (opponent shots for/game + own team shots against/game) / 2
  expected saves             = expected shots x league save percentage
  A game is watched if either goalie's expected shots is SHOT_THRESHOLD or more away
  from the league average. If the stats can't be loaded, every game is watched.
"""

import csv
import html
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

API = "https://api.the-odds-api.com/v4"
SPORT = "icehockey_nhl"
MARKET = "player_total_saves"
BOOK_SHORT = {"draftkings": "DK", "fanduel": "FD"}
LOCAL_TZ = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
PICKS_FILE = os.path.join(HERE, "picks.csv")
NOTES_FILE = os.path.join(HERE, "notes.csv")  # your "note ..." messages, read by the daily review
NOTE_FIELDS = ["noted_at", "date", "goalie", "team", "game", "tag", "line", "expected_saves", "note", "event_id"]
PICK_FIELDS = ["date", "game", "goalie", "team", "book", "line", "over_odds", "under_odds",
               "expected_saves", "tag", "actual_saves", "outcome", "result",
               "event_id", "commence_time", "away_team", "home_team", "logged_at", "fire",
               "taken", "taken_line", "taken_result", "taken_at",
               "key_out",
               "shadow_a_exp", "shadow_a_tag", "shadow_b_exp", "shadow_b_tag",
               "matchup", "warn"]  # 🎯 UNDER/OVER when both raw ranks are top/bottom MATCHUP_RANK (Oct 24)  # key players injured when the line was logged, e.g. "WSH:Ovechkin;NYR:"  # taken_* = bets you logged with "in"
GRADE_AFTER_HOUR = 7  # grade yesterday's games once it's past 7 AM Eastern
GOALIES_PER_GAME = 2


def env_int(name, default):
    return int(os.getenv(name, "") or default)


ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SILENT = (os.getenv("TELEGRAM_SILENT", "") or "false").strip().lower() in ("1", "true", "yes")
TEAMS = [t.strip().lower() for t in os.getenv("TEAMS", "").split(",") if t.strip()]
BOOKS = [b.strip().lower() for b in (os.getenv("BOOKS", "") or "draftkings,fanduel").split(",") if b.strip()]
LOOKAHEAD_HOURS = env_int("LOOKAHEAD_HOURS", 30)
RECHECK_MINUTES = env_int("RECHECK_MINUTES", 60)
RECHECK_WINDOW_HOURS = env_int("RECHECK_WINDOW_HOURS", 10)
RECHECK_RESERVE = env_int("RECHECK_RESERVE", 150)
# Goalies with no lean (always "no edge") are rechecked this often while missing; 0 = never.
NOLEAN_RECHECK_MINUTES = 15  # paid plan (20K credits); use 180 on the free 500-credit plan
# Last-30-minute watch (owner Oct 24, waiting on Carolina's goalie): games with a team ranked
# top/bottom PRIORITY_RANK in shots-for or shots-against get checked EVERY run (every minute) in the
# last PRIORITY_WINDOW minutes before puck drop while a goalie is still missing (~1 credit each).
PRIORITY_RANK = 3
PRIORITY_WINDOW = 30
FINAL_CHECKS = (45, 20)  # minutes before puck drop: any game still missing a goalie gets a check at each
SKIP_MIDDLING_GAMES = False  # True = don't check games where neither goalie has a lean
MIN_CREDITS = env_int("MIN_CREDITS", 20)
SHOT_THRESHOLD = float(os.getenv("SHOT_THRESHOLD", "") or "2")
LEAN_SAVES = float(os.getenv("TARGET_SAVES", "") or "1")
NHL_STATS_URL = "https://api.nhle.com/stats/rest/en/team/summary"
NHL_WEB = "https://api-web.nhle.com/v1"
STATS_REFRESH = timedelta(hours=6)
# Home/road blend: weight on a team's home (or road) split = split games / (split games + this).
# 5 -> 1 game 17%, 5 games 50%, 10 games 67%, 20 games 80%. Lower = trust splits sooner.
HOME_ROAD_K = 5
# Home/road nudge (owner approved Oct 21 after testing 182 goalie-games, confirmed on Oct 14-20 games
# the idea wasn't built on): home goalies face this many fewer shots, road goalies this many more.
# Tested 0.5-2.5; 1.0-1.5 best (1.5: 63-36 overall vs 46-34 without), 2+ overshoots.
HOME_ADJ = 0.0   # home goalie: shots taken off (Oct 21-26 was 1.5; dropped Oct 26 — home goalies have
                 # faced exactly what the base model expects since Oct 14)
ROAD_ADJ = 1.5   # road goalie: shots added (held every week: +1.6, +1.5, +1.9 vs expected)
STATS_VERSION = 5  # bump when the saved stats format changes
OPPONENT_ADJUST = True  # rate shots for/against vs. the strength of opponents faced
# Shadow models (Oct 14): logged to picks.csv next to the live numbers, never shown in alerts.
# Reviewed after ~2 weeks; the owner decides whether either replaces the live model.
#  A = shrink early-season team numbers toward league average (SHADOW_A_K phantom average games)
#      with a lower lean bar (SHADOW_A_THRESHOLD shots), since shrinking pulls everyone toward average.
#  B = (Oct 14-21) live + home/road nudge; since Oct 21 = the old model without the live nudge (HOME_ADJ/ROAD_ADJ backed out).
SHADOW_A_K = 2
SHADOW_A_THRESHOLD = 1.5
H2H_GAMES = 4           # head-to-head meetings shown in each alert (0 = hide)
H2H_SEASONS = 3         # how many seasons back to look for meetings
ROSTER_REFRESH = timedelta(hours=12)
TEST_PUSH = os.getenv("TEST_PUSH", "").strip().lower() in ("1", "true", "yes")


# ---------- helpers ----------

def iso(dt_obj):
    return dt_obj.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fmt_odds(price):
    if price is None:
        return "—"
    price = int(round(price))
    return f"+{price}" if price > 0 else str(price)


def fmt_time(commence, now=None):
    """'7:10PM' for a game today (Eastern); 'Sun 7:10PM' if it's another day."""
    local = parse_iso(commence).astimezone(LOCAL_TZ)
    today = (now or datetime.now(timezone.utc)).astimezone(LOCAL_TZ).date()
    t = local.strftime("%-I:%M%p")
    return t if local.date() == today else f"{local.strftime('%a')} {t}"


def api_get(path, params):
    """GET from The Odds API. Returns (data, remaining_credits or None)."""
    params = dict(params, apiKey=ODDS_API_KEY)
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "nhl-saves-alerts/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            remaining = resp.headers.get("x-requests-remaining")
            data = json.loads(resp.read().decode("utf-8"))
            return data, (int(float(remaining)) if remaining not in (None, "") else None)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        if e.code == 401:
            sys.exit(f"The Odds API rejected the key (401). Check the ODDS_API_KEY secret. {body}")
        if e.code == 404:
            return None, None  # event no longer listed
        if e.code == 429:
            print("Rate limited by The Odds API (429); will try again next run.")
            return None, None
        raise


UL, UL_END = "\x01", "\x02"  # underline markers used inside alert text


def ul(label):
    """Underline a label in an alert, e.g. ul('VGK L5 For:')."""
    return f"{UL}{label}{UL_END}"


LINK, LINK_MID, LINK_END = "\x03", "\x04", "\x05"  # tap-to-bet link markers


def link(label, url):
    """A word you can tap to open that bet on your DK/FD slip (owner Oct 17). No url = plain word."""
    return f"{LINK}{url}{LINK_MID}{label}{LINK_END}" if url else label


def plain(text):
    text = re.sub(f"{LINK}[^{LINK_MID}]*{LINK_MID}", "", text).replace(LINK_END, "")
    return text.replace(UL, "").replace(UL_END, "")


def to_html(text):
    """Telegram HTML for text with ul() underlines and link() tap-to-bet links."""
    body = html.escape(text, quote=False).replace(UL, "<u>").replace(UL_END, "</u>")
    return re.sub(f"{LINK}([^{LINK_MID}]*){LINK_MID}([^{LINK_END}]*){LINK_END}",
                  r'<a href="\1">\2</a>', body)


def send_push(title, message, silent=None, chat_id=None, reply_to=None):
    """Send a Telegram message from your bot to your chat. Text with ul() labels is sent as HTML
    so the labels show underlined."""
    text = f"{title}\n{message}" if title else message
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print(f"[dry run, no Telegram keys] {plain(text)}\n")
        return
    fields = {
        "chat_id": chat_id or TELEGRAM_CHAT_ID,
        "text": text[:4096],
        "disable_notification": "true" if (SILENT if silent is None else silent) else "false",
        "disable_web_page_preview": "true",
    }
    if reply_to:
        fields["reply_to_message_id"] = reply_to
    if UL in text or LINK in text:
        fields["text"] = to_html(text)[:4096]
        fields["parse_mode"] = "HTML"
    payload = urllib.parse.urlencode(fields).encode("utf-8")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(url, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if not result.get("ok"):
                print(f"Telegram error: {result}")
                return None
            return (result.get("result") or {}).get("message_id")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        sys.exit(f"Telegram rejected the message ({e.code}). Check TELEGRAM_BOT_TOKEN and "
                 f"TELEGRAM_CHAT_ID, and make sure you've sent your bot a message first. {detail}")


def migrate_event(rec):
    """Convert a game record from the old one-alert-per-book format."""
    if "lines" in rec:
        return rec
    posted = rec.pop("posted", {})
    rec["lines"] = {book: info.get("lines", {}) for book, info in posted.items()}
    rec["last_paid_check"] = max((info["at"] for info in posted.values() if info.get("at")),
                                 default=None)
    return rec


def load_state():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    state.setdefault("events", {})
    state.setdefault("low_credit_warned", False)
    state.setdefault("sent", {})  # Telegram message id -> which goalie alert it was (for "in" replies)
    for rec in state["events"].values():
        migrate_event(rec)
    return state


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def extract_lines(event_odds):
    """Return {book: {player: {"point": x, "over": price, "under": price}}}."""
    out = {}
    for bm in (event_odds or {}).get("bookmakers", []):
        book = bm.get("key")
        if book not in BOOKS:
            continue
        for market in bm.get("markets", []):
            if market.get("key") != MARKET:
                continue
            for o in market.get("outcomes", []):
                player = o.get("description") or "Unknown"
                entry = out.setdefault(book, {}).setdefault(player, {"point": o.get("point")})
                side = (o.get("name") or "").lower()
                if side in ("over", "under"):
                    entry[side] = o.get("price")
                    if o.get("link"):
                        entry[f"{side}_link"] = o["link"]  # opens this bet on your slip
                    if o.get("point") is not None:
                        entry["point"] = o.get("point")
    return out


def team_key(name):
    """'Montréal Canadiens' / 'St. Louis Blues' -> 'montrealcanadiens' / 'stlouisblues'."""
    plain = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", plain.lower())


def nickname(name):
    return (name or "").split()[-1]


def season_id(now):
    y = now.astimezone(LOCAL_TZ).year
    return f"{y}{y + 1}" if now.astimezone(LOCAL_TZ).month >= 8 else f"{y - 1}{y}"


def fetch_team_rows(now, extra=""):
    exp = f"seasonId={season_id(now)} and gameTypeId=2" + (f" and {extra}" if extra else "")
    params = urllib.parse.urlencode({"cayenneExp": exp})
    req = urllib.request.Request(f"{NHL_STATS_URL}?{params}",
                                 headers={"User-Agent": "nhl-saves-alerts/2.3"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    return raw.get("data", []) if isinstance(raw, dict) else raw


def split_stats(rows):
    out = {}
    for r in rows:
        gp = r.get("gamesPlayed") or 0
        sf, sa = r.get("shotsForPerGame"), r.get("shotsAgainstPerGame")
        if gp and sf is not None and sa is not None:
            out[team_key(r.get("teamFullName"))] = {"sf": sf, "sa": sa, "gp": gp}
    return out


def fetch_shot_stats(now):
    """Pull this season's team shots for/against (overall, home, road) from the NHL's free stats feed."""
    rows = fetch_team_rows(now)
    teams, shots_against, goals_against = {}, 0.0, 0.0
    for r in rows:
        gp = r.get("gamesPlayed") or 0
        sf, sa = r.get("shotsForPerGame"), r.get("shotsAgainstPerGame")
        if not gp or sf is None or sa is None:
            continue
        teams[team_key(r.get("teamFullName"))] = {"sf": sf, "sa": sa, "gp": gp}
        shots_against += sa * gp
        goals_against += r.get("goalsAgainst") or 0
    if len(teams) < 20:
        return None  # season hasn't really started; don't filter
    try:
        home = split_stats(fetch_team_rows(now, 'homeRoad="H"'))
        road = split_stats(fetch_team_rows(now, 'homeRoad="R"'))
    except Exception as e:  # splits are a refinement; overall numbers still work
        print(f"Couldn't load home/road splits ({e}); using overall numbers.")
        home, road = {}, {}
    for key, t in teams.items():
        t["home"], t["road"] = home.get(key), road.get(key)
    avg = sum(t["sf"] for t in teams.values()) / len(teams)
    sv = 1 - goals_against / shots_against if shots_against else 0.9
    raw = {k: {"sf": t["sf"], "sa": t["sa"]} for k, t in teams.items()}  # unadjusted, for rank display
    return {"fetched": iso(now), "season": season_id(now), "teams": teams, "raw": raw,
            "avg_shots": round(avg, 2), "save_pct": round(sv, 4), "version": STATS_VERSION}


def update_game_log(state, now):
    """Keep a log of every finished regular-season game this season: [date, away, home, away_sog, home_sog].
    Each date is fetched once from the NHL scores feed; only new dates are pulled."""
    season = season_id(now)
    log = state.get("game_log")
    if not log or log.get("season") != season:
        log = {"season": season, "dates_done": [], "games": []}
    done = set(log["dates_done"])
    start = datetime(int(season[:4]), 9, 25, tzinfo=LOCAL_TZ).date()
    yesterday = (now.astimezone(LOCAL_TZ) - timedelta(days=1)).date()
    day = start
    while day <= yesterday:
        ds = day.strftime("%Y-%m-%d")
        if ds not in done:
            games = nhl_get(f"{NHL_WEB}/score/{ds}").get("games", [])
            complete = True
            for g in games:
                if g.get("gameType") != 2 or g.get("gameScheduleState", "OK") != "OK":
                    continue
                if g.get("gameState") not in ("OFF", "FINAL"):
                    complete = False
                    continue
                a, h = g["awayTeam"], g["homeTeam"]
                if a.get("sog") is None or h.get("sog") is None:
                    complete = False
                    continue
                log["games"].append([ds, a["abbrev"], h["abbrev"], a["sog"], h["sog"]])
            if complete:
                log["dates_done"].append(ds)
            else:  # try this date again next refresh; drop partial rows to avoid duplicates
                log["games"] = [x for x in log["games"] if x[0] != ds]
        day += timedelta(days=1)
    state["game_log"] = log
    return log["games"]


def adjusted_team_stats(games, abbrev_to_key, shrink=0):
    """Opponent-adjusted shots for/against per team, overall and home/road, from the game log.
    shrink > 0 adds that many league-average games to every average (shadow model A)."""
    by_team = {}
    for ds, away, home, a_sog, h_sog in games:
        by_team.setdefault(away, []).append({"opp": home, "sf": a_sog, "sa": h_sog, "home": False})
        by_team.setdefault(home, []).append({"opp": away, "sf": h_sog, "sa": a_sog, "home": True})
    n = sum(len(v) for v in by_team.values())
    if not n:
        return None, None
    lg = sum(g["sf"] for v in by_team.values() for g in v) / n

    def opp_avg(opp, stat, excluding):
        vals = [g[stat] for g in by_team.get(opp, []) if g["opp"] != excluding]
        if not vals:  # only played this team so far: fall back to all its games, then league avg
            vals = [g[stat] for g in by_team.get(opp, [])]
        return (sum(vals) + shrink * lg) / (len(vals) + shrink) if vals else lg

    teams = {}
    for team, glist in by_team.items():
        rows = []
        for g in glist:
            sf_adj = g["sf"] - (opp_avg(g["opp"], "sa", team) - lg)  # vs. how much opp usually allows
            sa_adj = g["sa"] - (opp_avg(g["opp"], "sf", team) - lg)  # vs. how much opp usually shoots
            rows.append((sf_adj, sa_adj, g["home"]))

        def summary(sub):
            return ({"sf": (sum(r[0] for r in sub) + shrink * lg) / (len(sub) + shrink),
                     "sa": (sum(r[1] for r in sub) + shrink * lg) / (len(sub) + shrink),
                     "gp": len(sub)} if sub else None)
        key = abbrev_to_key.get(team)
        if not key:
            continue
        t = summary(rows)
        t["home"] = summary([r for r in rows if r[2]])
        t["road"] = summary([r for r in rows if not r[2]])
        teams[key] = t
    return teams, lg


def load_h2h(away, home, now):
    """Last H2H_GAMES meetings (regular season + playoffs), newest first:
    [[date, away_abbrev, home_abbrev, away_sog, home_sog], ...]"""
    y = int(season_id(now)[:4])
    meetings = []
    for k in range(H2H_SEASONS):
        sched = nhl_get(f"{NHL_WEB}/club-schedule-season/{away}/{y - k}{y - k + 1}").get("games", [])
        for g in sched:
            teams = {g.get("awayTeam", {}).get("abbrev"), g.get("homeTeam", {}).get("abbrev")}
            if (teams == {away, home} and g.get("gameType") in (2, 3)
                    and g.get("gameState") in ("OFF", "FINAL")):
                meetings.append((g["gameDate"], g["id"]))
        if len(meetings) >= H2H_GAMES:
            break
    out = []
    for date, gid in sorted(meetings, reverse=True)[:H2H_GAMES]:
        box = nhl_get(f"{NHL_WEB}/gamecenter/{gid}/boxscore")
        a, h = box.get("awayTeam", {}), box.get("homeTeam", {})
        if a.get("sog") is not None and h.get("sog") is not None:
            out.append([date, a["abbrev"], h["abbrev"], a["sog"], h["sog"]])
    return out


def get_h2h(state, away, home, now):
    if H2H_GAMES <= 0 or not away or not home:
        return []
    return cached(state, f"h2h_{'-'.join(sorted((away, home)))}", now, timedelta(hours=12),
                  lambda: load_h2h(away, home, now)) or []


def fmt_h2h(h2h, ab, side=None):
    """Shots on this goalie's team in recent meetings, newest first:
    'H2H L4 on MIN 31, 16, @25, @24 (avg 24.0)'; @ = the shooting team was on the road
    (game at MIN). With no side given, both teams' lines."""
    if not h2h:
        return []
    lines = []
    for i, team in enumerate([ab[side]] if side else (ab["away"], ab["home"])):
        shooter = ab["home"] if team == ab["away"] else ab["away"]
        faced = [(g[4] if g[1] == team else g[3]) for g in h2h]  # opponent's shots = shots on this goalie
        nums = ", ".join(("@" if g[1] == shooter else "") + str(x) for g, x in zip(h2h, faced))  # @ = shooting team on the road
        lines.append(f"{ul(f'H2H L{len(h2h)} on {team}:')} {nums} (avg {sum(faced) / len(faced):.1f})")
    return lines


def get_shot_stats(state, now):
    saved = state.get("shot_stats")
    if saved and now - parse_iso(saved["fetched"]) < STATS_REFRESH \
            and saved.get("season") == season_id(now) and saved.get("version") == STATS_VERSION:
        return saved
    try:
        fresh = fetch_shot_stats(now)
    except Exception as e:  # network hiccup: fall back to the last good copy
        print(f"Couldn't load NHL team stats ({e}); using last saved copy if any.")
        return saved
    if fresh and OPPONENT_ADJUST:
        try:
            abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
            games = update_game_log(state, now)
            ab_map = {ab: key for key, ab in abbrevs.items()}
            teams, lg = adjusted_team_stats(games, ab_map)
            if teams and len(teams) >= 20:
                fresh.update(teams=teams, avg_shots=round(lg, 2), adjusted=True)
                fresh["teams_shadow_a"] = adjusted_team_stats(games, ab_map, SHADOW_A_K)[0]
        except Exception as e:  # adjustment is a refinement; raw numbers still work
            print(f"Couldn't build opponent adjustment ({e}); using raw team numbers.")
    if fresh:
        state["shot_stats"] = fresh
    return fresh or saved


def blend(team, split, stat):
    """Mix a team's home or road number into its overall number, trusting it more as games add up."""
    sp = team.get(split) or {}
    gp = sp.get("gp", 0)
    if not gp:
        return team[stat]
    w = gp / (gp + HOME_ROAD_K)
    return w * sp[stat] + (1 - w) * team[stat]


def matchup(event, stats):
    """Expected shots/saves on each goalie, or None if a team is missing from the stats."""
    if not stats:
        return None
    home = stats["teams"].get(team_key(event["home_team"]))
    away = stats["teams"].get(team_key(event["away_team"]))
    if not (home and away):
        return None
    avg, sv = stats["avg_shots"], stats["save_pct"]
    out = {}
    for side, own, opp, name in (("home", home, away, event["home_team"]),
                                 ("away", away, home, event["away_team"])):
        own_split, opp_split = ("home", "road") if side == "home" else ("road", "home")
        shots = (blend(opp, opp_split, "sf") + blend(own, own_split, "sa")) / 2
        shots += -HOME_ADJ if side == "home" else ROAD_ADJ
        out[side] = {"team": nickname(name), "shots": shots, "saves": shots * sv,
                     "delta": shots - avg}
    return out


def shadow_numbers(event, stats, m, side, point):
    """Shadow models A and B for one goalie: {'shadow_a_exp', 'shadow_a_tag', ...} (blank if unknown).
    Logged only; alerts and records use the live model."""
    out = {}
    if not (stats and m and side) or point is None:
        return out
    avg, sv = stats["avg_shots"], stats["save_pct"]
    teams = stats.get("teams_shadow_a") or {}
    own = teams.get(team_key(event[f"{side}_team"]))
    opp = teams.get(team_key(event["away_team" if side == "home" else "home_team"]))
    if own and opp:
        own_split, opp_split = ("home", "road") if side == "home" else ("road", "home")
        shots = (blend(opp, opp_split, "sf") + blend(own, own_split, "sa")) / 2
        out["shadow_a_exp"] = f"{shots * sv:.1f}"
        out["shadow_a_tag"] = tag_code(shots * sv, point, shots - avg, SHADOW_A_THRESHOLD)
    shots = m[side]["shots"] + (HOME_ADJ if side == "home" else -ROAD_ADJ)  # back out the nudge
    out["shadow_b_exp"] = f"{shots * sv:.1f}"
    out["shadow_b_tag"] = tag_code(shots * sv, point, shots - avg)
    return out


def nhl_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nhl-saves-alerts/2.2"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cached(state, key, now, max_age, loader):
    """Return state[key]['value'], reloading it when older than max_age."""
    entry = state.get(key)
    if entry and now - parse_iso(entry["fetched"]) < max_age:
        return entry["value"]
    try:
        value = loader()
    except Exception as e:
        print(f"Couldn't load {key} ({e}); using last saved copy if any.")
        return entry["value"] if entry else None
    state[key] = {"fetched": iso(now), "value": value}
    return value


def load_abbrevs():
    data = nhl_get(f"{NHL_WEB}/standings/now")
    return {team_key(t["teamName"]["default"]): t["teamAbbrev"]["default"]
            for t in data.get("standings", [])}


def load_goalies(abbrev):
    data = nhl_get(f"{NHL_WEB}/roster/{abbrev}/current")
    return [f"{g['firstName']['default']} {g['lastName']['default']}"
            for g in data.get("goalies", [])]


def goalie_sides(event, players, state, now):
    """Map goalie name -> 'home'/'away' using current NHL rosters."""
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    rosters = {}
    for side in ("home", "away"):
        ab = abbrevs.get(team_key(event[f"{side}_team"]))
        if ab:
            rosters[side] = cached(state, f"roster_{ab}", now, ROSTER_REFRESH,
                                   lambda ab=ab: load_goalies(ab)) or []
    out = {}
    for p in players:
        pk = team_key(p)
        last = team_key(p.split()[-1]) if p.split() else ""
        for side, names in rosters.items():
            if any(team_key(n) == pk for n in names):
                out[p] = side
        if p not in out:  # fall back to a unique last-name match
            hits = [s for s, names in rosters.items()
                    if any(team_key(n.split()[-1]) == last for n in names)]
            if len(hits) == 1:
                out[p] = hits[0]
    return out


def tag_code(expected, point, delta, threshold=None):
    """The matchup picks the direction; the line picks the strength.
    delta = goalie's expected shots minus league average.
      delta >= +SHOT_THRESHOLD (overs only):  line <= expected -> OVER,
          line within LEAN_SAVES above expected -> LEAN_OVER, else FADE (never an under)
      delta <= -SHOT_THRESHOLD (unders only): mirror image -> UNDER / LEAN_UNDER / FADE
      otherwise (middling): FADE"""
    if expected is None or point is None or delta is None:
        return ""
    edge = max(SHOT_THRESHOLD if threshold is None else threshold, 0.01)
    if delta >= edge:
        if point <= expected:
            return "OVER"
        return "LEAN_OVER" if point <= expected + LEAN_SAVES else "FADE"
    if delta <= -edge:
        if point >= expected:
            return "UNDER"
        return "LEAN_UNDER" if point >= expected - LEAN_SAVES else "FADE"
    return "FADE"


TAG_LABELS = {"OVER": "OVER", "LEAN_OVER": "LEAN OVER", "UNDER": "UNDER",
              "LEAN_UNDER": "LEAN UNDER", "FADE": "NO EDGE"}
BET_SIDE = {"OVER": "OVER", "LEAN_OVER": "OVER", "UNDER": "UNDER", "LEAN_UNDER": "UNDER"}


FIRE_GAP = 2.0   # 🔥 needs expected saves at least this far past the line (OVER/UNDER only)
FIRE_RANK = 10   # ...and a raw shots rank in the top/bottom this many


def is_fire(code, expected, point, side, ctx):
    """🔥 = an OVER/UNDER where three things agree:
      1. expected saves are FIRE_GAP+ past the line,
      2. H2H: this goalie's team faced above-average shots in recent meetings (over) / below (under),
      3. raw ranks: opponent shots-for or own shots-against is top-FIRE_RANK (over) / bottom-FIRE_RANK (under)."""
    if code not in ("OVER", "UNDER") or not ctx or not side or expected is None or point is None:
        return False
    over = code == "OVER"
    if (expected - point if over else point - expected) < FIRE_GAP:
        return False
    event, ab, h2h, raw, lg = ctx["event"], ctx["ab"], ctx.get("h2h"), ctx.get("raw"), ctx.get("lg")
    if not h2h or not raw or lg is None:
        return False
    team = ab[side]
    faced = [(g[4] if g[1] == team else g[3]) for g in h2h]
    h2h_avg = sum(faced) / len(faced)
    if (h2h_avg <= lg) if over else (h2h_avg >= lg):
        return False
    other = "home" if side == "away" else "away"
    opp, own = team_key(event[f"{other}_team"]), team_key(event[f"{side}_team"])
    if opp not in raw or own not in raw:
        return False
    def rank(key, stat, most):
        v = raw[key][stat]
        return 1 + sum(1 for t in raw.values() if (t[stat] > v if most else t[stat] < v))
    return (rank(opp, "sf", over) <= FIRE_RANK) or (rank(own, "sa", over) <= FIRE_RANK)


def fire_context(event, ab, h2h, raw, m):
    side = "away"
    lg = (m[side]["shots"] - m[side]["delta"]) if m else None
    return {"event": event, "ab": ab, "h2h": h2h, "raw": raw, "lg": lg}


def target_tag(expected, point, delta, side=None, ctx=None, ln=None):
    """' UNDER 🔥' etc. With the book's line (ln), the tag word is a tap-to-bet link for that side;
    NO EDGE (or no tag) gets ' O/U' where O and U each open that bet (owner Oct 17)."""
    code = tag_code(expected, point, delta)
    ln = ln or {}
    if code in BET_SIDE:
        fire = " 🔥" if is_fire(code, expected, point, side, ctx) else ""
        return f" {link(TAG_LABELS[code], ln.get(BET_SIDE[code].lower() + '_link'))}{fire}"
    ou = (f" {link('O', ln.get('over_link'))}/{link('U', ln.get('under_link'))}"
          if ln.get("over_link") or ln.get("under_link") else "")
    return (f" {TAG_LABELS[code]}" if code else "") + ou


# ---------- pick log & grading ----------

def load_picks():
    try:
        with open(PICKS_FILE, newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def save_picks(rows):
    with open(PICKS_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PICK_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def log_picks(event, new_pairs, lines, m, sides, abbrevs, now, h2h=None, raw=None, injuries=None, stats=None):
    """Append one row per newly posted (book, goalie) line."""
    rows = load_picks()
    seen = {(r["event_id"], r["goalie"], r["book"]) for r in rows}
    date = parse_iso(event["commence_time"]).astimezone(LOCAL_TZ).strftime("%Y-%m-%d")
    game = f"{nickname(event['away_team'])} @ {nickname(event['home_team'])}"
    ab = {s: abbrevs.get(team_key(event[f"{s}_team"])) or nickname(event[f"{s}_team"])
          for s in ("away", "home")}
    ctx = fire_context(event, ab, h2h, raw, m)
    for book, player in sorted(new_pairs):
        if (event["id"], player, BOOK_SHORT.get(book, book)) in seen:
            continue
        ln = lines.get(book, {}).get(player, {})
        side = sides.get(player)
        expected = m[side]["saves"] if (m and side) else None
        team = abbrevs.get(team_key(event[f"{side}_team"]), "") if side else ""
        rows.append({
            "date": date, "game": game, "goalie": player, "team": team,
            "book": BOOK_SHORT.get(book, book), "line": ln.get("point"),
            "over_odds": fmt_odds(ln.get("over")), "under_odds": fmt_odds(ln.get("under")),
            "expected_saves": f"{expected:.1f}" if expected is not None else "",
            "tag": tag_code(expected, ln.get("point"), m[side]["delta"] if (m and side) else None),
            "fire": "1" if is_fire(tag_code(expected, ln.get("point"), m[side]["delta"] if (m and side) else None),
                                   expected, ln.get("point"), side, ctx) else "",
            "event_id": event["id"], "commence_time": event["commence_time"],
            "away_team": event["away_team"], "home_team": event["home_team"],
            "logged_at": iso(now),
            "key_out": key_out_summary(injuries or {}, ab),
            **shadow_numbers(event, stats, m, side, ln.get("point")),
            "matchup": matchup_marker(event, side, raw),
            "warn": rank_warning(event, side, ab, raw, m[side]["delta"] if (m and side) else None),
        })
    save_picks(rows)


def boxscore_goalies(game_id):
    """{(team_abbrev, last_name_key, first_initial): (saves, played)} for a finished game."""
    box = nhl_get(f"{NHL_WEB}/gamecenter/{game_id}/boxscore")
    out = {}
    for side in ("awayTeam", "homeTeam"):
        abbrev = box.get(side, {}).get("abbrev", "")
        for g in box.get("playerByGameStats", {}).get(side, {}).get("goalies", []):
            name = g.get("name", {}).get("default", "")  # e.g. "J. Markstrom"
            first, _, last = name.partition(" ")
            played = (g.get("toi") or "00:00") != "00:00"
            out[(abbrev, team_key(last), first[:1].lower())] = (g.get("saves") or 0, played)
    return out


def find_goalie(box, player, team):
    parts = player.split()
    last, initial = team_key(parts[-1]) if parts else "", (parts[0][:1].lower() if parts else "")
    hits = [v for (ab, ln, fi), v in box.items()
            if ln == last and (not team or ab == team)]
    if len(hits) > 1:
        hits = [v for (ab, ln, fi), v in box.items()
                if ln == last and fi == initial and (not team or ab == team)]
    return hits[0] if len(hits) == 1 else None


def grade_row(r, abbrevs, schedules, boxes):
    """Grade one pick-log row from the NHL feed. True if graded, False if the game isn't final yet."""
    if r["date"] not in schedules:
        schedules[r["date"]] = nhl_get(f"{NHL_WEB}/score/{r['date']}").get("games", [])
    away = abbrevs.get(team_key(r["away_team"]))
    home = abbrevs.get(team_key(r["home_team"]))
    game = next((g for g in schedules[r["date"]]
                 if g["awayTeam"]["abbrev"] == away and g["homeTeam"]["abbrev"] == home), None)
    if not game:
        return False
    if game.get("gameScheduleState", "OK") != "OK":
        r.update(outcome="VOID", result="VOID")  # postponed / cancelled
        grade_taken(r)
        return True
    if game.get("gameState") not in ("OFF", "FINAL"):
        return False
    if game["id"] not in boxes:
        boxes[game["id"]] = boxscore_goalies(game["id"])
    hit = find_goalie(boxes[game["id"]], r["goalie"], r.get("team"))
    if not hit or not hit[1]:
        r.update(actual_saves="", outcome="VOID", result="VOID")  # didn't play
    else:
        saves, line = hit[0], float(r["line"])
        outcome = "OVER" if saves > line else "UNDER" if saves < line else "PUSH"
        if r["tag"] in BET_SIDE:
            result = "P" if outcome == "PUSH" else ("W" if outcome == BET_SIDE[r["tag"]] else "L")
        else:
            result = "-"  # no edge / untagged: recorded, not scored
        r.update(actual_saves=saves, outcome=outcome, result=result)
    grade_taken(r)
    return True


def grade_picks(state, now):
    """Grade picks from games before today (Eastern) using NHL box scores. Returns newly graded rows."""
    local_now = now.astimezone(LOCAL_TZ)
    if local_now.hour < GRADE_AFTER_HOUR:
        return []
    today = local_now.strftime("%Y-%m-%d")
    rows = load_picks()
    pending = [r for r in rows if not r.get("result") and r["date"] < today]
    if not pending:
        return []
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    schedules, boxes, graded = {}, {}, []
    for r in pending:
        try:
            if grade_row(r, abbrevs, schedules, boxes):
                graded.append(r)
        except Exception as e:
            print(f"Couldn't grade {r['goalie']} ({e}); will retry next run.")
    if graded:
        save_picks(rows)
    return graded


RECHECK_DAYS = 2  # each morning, re-read the box scores of the last 2 nights to catch stat corrections


def recheck_corrections(state, now):
    """Stat corrections (owner Oct 15): the NHL sometimes changes saves after the final horn, even
    the next morning. Each morning (after GRADE_AFTER_HOUR) re-read the box score for every pick
    graded in the last RECHECK_DAYS nights; if saves changed, regrade (records update) and text:
    '🔁 Stat correction: Wolf (CGY) now 25 saves (was 24) · your o24.5 ❌ → ✅'."""
    local = now.astimezone(LOCAL_TZ)
    today = local.strftime("%Y-%m-%d")
    if local.hour < GRADE_AFTER_HOUR or state.get("corrections_checked") == today:
        return
    since = (local - timedelta(days=RECHECK_DAYS)).strftime("%Y-%m-%d")
    rows = load_picks()
    recent = [r for r in rows if since <= r["date"] < today and r.get("result")
              and r.get("result") != "VOID" and r.get("actual_saves") not in (None, "")]
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    schedules, boxes, changed = {}, {}, {}
    for r in recent:
        before = {k: r.get(k) for k in ("actual_saves", "outcome", "result", "taken_result")}
        r.update(actual_saves="", outcome="", result="", taken_result="")
        try:
            ok = grade_row(r, abbrevs, schedules, boxes)
        except Exception as e:
            print(f"Couldn't recheck {r['goalie']} ({e}).")
            ok = False
        if not ok or r.get("actual_saves") in (None, ""):
            r.update(before)  # couldn't read it now: keep what we had
            continue
        if str(r["actual_saves"]) != str(before["actual_saves"]):
            changed.setdefault((r["event_id"], r["goalie"]), []).append((r, before))
    state["corrections_checked"] = today
    if not changed:
        return
    save_picks(rows)
    lines = []
    for (event_id, goalie), pairs in changed.items():
        r, before = pairs[0]
        name = f"{last_name(goalie)} ({r['team']})" if r.get("team") else last_name(goalie)
        line = f"{name} now {r['actual_saves']} saves (was {before['actual_saves']})"
        flips = [f"your {x['taken'][0].lower()}{x['taken_line']} {MARKS.get(b['taken_result'], '?')} → "
                 f"{MARKS.get(x['taken_result'], '?')}" for x, b in pairs
                 if x.get("taken") and x.get("taken_result") != b.get("taken_result")]
        model = [f"model {x['line']} {MARKS.get(b['result'], b['result'])} → {MARKS.get(x['result'], x['result'])}"
                 for x, b in pairs if x.get("result") in ("W", "L", "P") or b.get("result") in ("W", "L", "P")
                 if x.get("result") != b.get("result")]
        lines.append(line + "".join(f" · {f}" for f in dict.fromkeys(flips + model)))
    send_push("", "🔁 Stat correction" + ("s" if len(lines) > 1 else "") + ":\n" + "\n".join(lines))
    for (event_id, goalie), pairs in changed.items():
        first = min((x for x, b in pairs if x.get("taken")), key=lambda x: x.get("taken_at", ""), default=None)
        if first:
            old = next(b for x, b in pairs if x is first)
            if old.get("taken_result") != first.get("taken_result"):
                channel_result(state, rows, event_id, goalie, correction_from=f"{old['actual_saves']} saves")
    print("CORRECTIONS " + " | ".join(lines))


CLOSE_CALL = 1  # live result within this many saves of your line: say it'll be rechecked


FINAL_CHECK_AFTER = timedelta(hours=2)  # start looking for a final this long after puck drop
MARKS = {"W": "✅", "L": "❌", "P": "push", "VOID": "void"}


def live_results(state, now):
    """Your bets, the minute a game ends: '✅ Wolf (CGY) o24.5: 28 saves' (owner Oct 15).
    Grades the goalies you bet (all their lines) right away so the record updates; the morning
    recap still lists them for the model but leaves them out of 'Your bets'."""
    rows = load_picks()
    pending = [r for r in rows if r.get("taken") and not r.get("result") and r.get("commence_time")
               and now - parse_iso(r["commence_time"]) >= FINAL_CHECK_AFTER]
    if not pending:
        return
    keys = {(r["event_id"], r["goalie"]) for r in pending}
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    schedules, boxes, done = {}, {}, []
    for key in sorted(keys):
        mine = [r for r in rows if (r["event_id"], r["goalie"]) == key and not r.get("result")]
        try:
            if not all(grade_row(r, abbrevs, schedules, boxes) for r in mine):
                continue
        except Exception as e:
            print(f"Couldn't grade {key[1]} live ({e}); will retry next run.")
            continue
        done.append(key)
    if not done:
        return
    save_picks(rows)
    night = state.setdefault("night_graded", {})
    for event_id, goalie in done:
        bets = sorted((r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie
                       and r.get("taken")), key=lambda r: r.get("taken_at", ""))
        r = bets[0]
        night.setdefault(r["date"], []).append(f"{event_id}|{goalie}")
        name = f"{last_name(goalie)} ({r['team']})" if r.get("team") else last_name(goalie)
        if all(b.get("taken_result") == "VOID" for b in bets):
            send_push("", f"{name} {r['taken'][0].lower()}{r['taken_line']}: didn't play (void)")
            continue
        plays = [f"{b['taken'][0].lower()}{b['taken_line']}" for b in bets]
        res = [b.get("taken_result") for b in bets]
        if len(set(res)) == 1:
            mark = MARKS.get(res[0], "")
            text = f"{mark} {name} " + " · ".join(plays) + f": {r['actual_saves']} saves"
        else:
            text = (f"{name} " + " · ".join(f"{p} {MARKS.get(x, '')}" for p, x in zip(plays, res))
                    + f": {r['actual_saves']} saves")
        if r.get("actual_saves") not in (None, "") and any(
                abs(float(r["actual_saves"]) - float(b["taken_line"])) <= CLOSE_CALL for b in bets):
            text += " (close, I'll recheck the official number in the morning)"
        send_push("", text)
        print(f"LIVE RESULT {text}")


def first_per_goalie(rows):
    """One row per goalie per game: the first line alerted (what you could bet first),
    so a goalie posted at both books, or at two different lines, counts once."""
    seen, out = set(), []
    for r in rows:
        key = (r["event_id"], r["goalie"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def record_line(rows, tag):
    """W-L-P for a tag, counting each goalie once per game."""
    w = l = p = 0
    for r in first_per_goalie(rows):
        if r.get("tag") != tag or r.get("result") not in ("W", "L", "P"):
            continue
        w += r["result"] == "W"; l += r["result"] == "L"; p += r["result"] == "P"
    return w, l, p


def no_edge_split(rows):
    """How NO EDGE lines landed, all season: 'NO EDGE 37% over 63% under (30)'.
    Each goalie counts once per game; pushes are counted separately."""
    o = u = p = 0
    for r in first_per_goalie(rows):
        if r.get("tag") != "FADE" or r.get("outcome") not in ("OVER", "UNDER", "PUSH"):
            continue
        o += r["outcome"] == "OVER"; u += r["outcome"] == "UNDER"; p += r["outcome"] == "PUSH"
    if not (o + u):
        return "NO EDGE no results yet"
    return (f"NO EDGE {o / (o + u):.0%} over {u / (o + u):.0%} under ({o + u}"
            + (f", {p} push" if p else "") + ")")


def fmt_record(w, l, p):
    if not (w or l or p):
        return "no picks yet"
    pct = f" ({w / (w + l):.0%})" if (w + l) else ""
    return f"{w}-{l}" + (f"-{p}" if p else "") + pct


def last_name(player):
    return player.split()[-1] if player and player.split() else player


def who(r, abbrevs):
    """'Shesterkin (NYR) vs. WSH' from a picks.csv row (falls back to last name only)."""
    name, team = last_name(r["goalie"]), r.get("team") or ""
    if not team:
        return name
    away = abbrevs.get(team_key(r.get("away_team", "")))
    home = abbrevs.get(team_key(r.get("home_team", "")))
    opp = home if team == away else away if team == home else None
    return f"{name} ({team})" + (f" vs. {opp}" if opp else "")


def results_message(graded, abbrevs=None, skip_bets=()):
    abbrevs = abbrevs or {}
    # One line per goalie; if his line differed between books (or moved), each line's
    # result follows the other: "Markstrom (FLA) vs. BUF u23.5 UNDER (DK) ✅ · u24.5 UNDER (FD) ✅: 9 saves"
    lines, done = [], set()
    ordered = sorted(graded, key=lambda r: (r["date"], r["game"], r["goalie"], r.get("logged_at", ""), r["book"]))
    for r in ordered:
        gkey = (r["event_id"], r["goalie"])
        if gkey in done:
            continue
        done.add(gkey)
        mine = [x for x in ordered if (x["event_id"], x["goalie"]) == gkey]
        if all(x["outcome"] == "VOID" for x in mine):
            lines.append(f"{who(r, abbrevs)}: didn't play (void)")
            continue
        parts, seen_lines = [], []
        for x in mine:
            if x["line"] in seen_lines:
                continue
            seen_lines.append(x["line"])
            books = "/".join(y["book"] for y in mine if y["line"] == x["line"])
            label = {"OVER": f"o{x['line']} OVER", "LEAN_OVER": f"o{x['line']} LEAN OVER",
                     "UNDER": f"u{x['line']} UNDER", "LEAN_UNDER": f"u{x['line']} LEAN UNDER"}.get(
                         x["tag"], f"{x['line']} NO EDGE")
            if x.get("fire") == "1":
                label += " 🔥"
            mark = {"W": " ✅", "L": " ❌", "P": " push"}.get(x["result"], f" → went {x['outcome'].lower()}")
            parts.append(f"{label} ({books}){mark}")
        lines.append(f"{who(r, abbrevs)} " + " · ".join(parts) + f": {r['actual_saves']} saves")
    all_rows = load_picks()
    season = " · ".join(f"{TAG_LABELS[t]} {fmt_record(*record_line(all_rows, t))}"
                        for t in ("OVER", "LEAN_OVER", "UNDER", "LEAN_UNDER"))
    fire_rows = [r for r in all_rows if r.get("fire") == "1"]
    season += " · 🔥 " + fmt_record(*[a + b for a, b in zip(record_line(fire_rows, "OVER"),
                                                          record_line(fire_rows, "UNDER"))])
    season += " · " + no_edge_split(all_rows)
    out = "\n".join(lines) + "\n\nSeason: " + season
    mine = [r for r in graded if r.get("taken") and f"{r['event_id']}|{r['goalie']}" not in skip_bets]
    if mine:
        out += "\n\nYour bets:\n" + "\n".join(
            f"{who(r, abbrevs)} {r['taken'][0].lower()}{r['taken_line']} ({r['book']}): "
            + ("didn't play (void)" if r["taken_result"] == "VOID" else
               f"{r['actual_saves']} saves" + {"W": " ✅", "L": " ❌", "P": " push"}.get(r["taken_result"], ""))
            for r in sorted(mine, key=lambda r: (r["date"], r["game"], r["goalie"])))
    w, l, p, bets = my_record(all_rows + past_bets())  # incl. bets from before logging
    if w or l or p:
        out += "\nYour season: " + fmt_record(w, l, p) + (f" ({bets} bets)" if bets != w + l + p else "")
    return out


def has_lean(m, side):
    """A goalie side has a lean when its expected shots are SHOT_THRESHOLD+ above or below average."""
    return abs(m[side]["delta"]) >= max(SHOT_THRESHOLD, 0.01)


def lean_goalie_missing(event, rec, m, state, now):
    """True if some book is still missing the goalie for a side that has a lean tonight.
    Missing no-lean goalies (always tagged no edge) are rechecked only every NOLEAN_RECHECK_MINUTES.
    If anything is unclear (no stats, a goalie we can't place on a team), say True to be safe."""
    if not m:
        return True
    lean_sides = {s for s in ("away", "home") if has_lean(m, s)}
    if not lean_sides:
        return False
    players = {p for pl in rec["lines"].values() for p in pl}
    sides = goalie_sides(event, players, state, now)
    if any(p not in sides for p in players):
        return True
    for book in BOOKS:
        posted = {sides[p] for p in rec["lines"].get(book, {})}
        if lean_sides - posted:
            return True
    return False


def watch_game(m):
    if SHOT_THRESHOLD <= 0 or m is None:
        return True
    return any(abs(g["delta"]) >= SHOT_THRESHOLD for g in m.values())


def fmt_matchup(m):
    if not m:
        return ""
    parts = []
    for side in ("away", "home"):
        g = m[side]
        parts.append(f"{g['team']} goalie ~{g['saves']:.1f} saves "
                     f"({g['shots']:.1f} shots, {g['delta']:+.1f} vs avg)")
    return "Expected: " + " · ".join(parts)


def wanted(event):
    if not TEAMS:
        return True
    teams = f"{event.get('home_team', '')} {event.get('away_team', '')}".lower()
    return any(t in teams for t in TEAMS)


def is_complete(rec):
    return all(len(rec["lines"].get(b, {})) >= GOALIES_PER_GAME for b in BOOKS)


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


RECENT_GAMES = 5  # games listed on the "L5 For / L5 Against" lines


def recent_games(games, team, stat, n=RECENT_GAMES):
    """Last n games for a team, newest first, as '43@TOR, 28SEA, ...' (@ = played on the road).
    stat 'sf' = shots the team took, 'sa' = shots it allowed. Raw numbers."""
    out = []
    for d, a, h, asog, hsog in sorted(games or [], key=lambda g: g[0], reverse=True):
        if team not in (a, h):
            continue
        away = team == a
        shots = (asog if away else hsog) if stat == "sf" else (hsog if away else asog)
        out.append(f"{shots}@{h}" if away else f"{shots}{a}")  # @ = team was on the road
        if len(out) == n:
            break
    return out


MATCHUP_RANK = 10  # 🎯 = opponent shots-for AND own shots-against both in the top/bottom this many


def priority_game(event, stats):
    """True if either team is top/bottom PRIORITY_RANK in raw shots-for or shots-against."""
    raw = (stats or {}).get("raw") or {}
    for key in (team_key(event["away_team"]), team_key(event["home_team"])):
        if key not in raw:
            continue
        for stat in ("sf", "sa"):
            v = raw[key][stat]
            most = 1 + sum(1 for x in raw.values() if x[stat] > v)
            least = 1 + sum(1 for x in raw.values() if x[stat] < v)
            if min(most, least) <= PRIORITY_RANK:
                return True
    return False


def matchup_marker(event, side, raw):
    """'UNDER' when the opponent is a bottom-10 shooting team AND this goalie's team is a bottom-10
    shots-allowed team (owner's Carolina-Vancouver read); 'OVER' for the mirror; else ''.
    Raw season ranks, same as the L5 lines. Shown as a 🎯 in alerts and logged in picks.csv
    `matchup` (owner Oct 24). Info only: tags are unchanged. Backtest Oct 7-23 (212 goalies):
    unders 14-6, overs 12-14; his own bets in these spots: unders 8-3, overs 4-5."""
    if not raw or not side:
        return ""
    other = "home" if side == "away" else "away"
    opp, own = team_key(event[f"{other}_team"]), team_key(event[f"{side}_team"])
    if opp not in raw or own not in raw:
        return ""
    def most(key, stat):
        return 1 + sum(1 for t in raw.values() if t[stat] > raw[key][stat])
    def least(key, stat):
        return 1 + sum(1 for t in raw.values() if t[stat] < raw[key][stat])
    if least(opp, "sf") <= MATCHUP_RANK and least(own, "sa") <= MATCHUP_RANK:
        return "UNDER"
    if most(opp, "sf") <= MATCHUP_RANK and most(own, "sa") <= MATCHUP_RANK:
        return "OVER"
    return ""


WARN_RANK = 5  # ⚠️ when a top/bottom-5 rank argues against the model's lean (owner Oct 24)


def rank_warning(event, side, ab, raw, delta):
    """'PHI 2nd most against' when a raw rank in the top/bottom WARN_RANK argues against the lean:
    under lean (delta <= -SHOT_THRESHOLD) but the opponent is a top-5 shooting team or this team a
    top-5 shots-allowed team; mirror for an over lean. No lean = no warning. Info only; logged in
    picks.csv `warn` so reviews can grade it (his own bets with a conflicting rank: 2-8 by Oct 24)."""
    if not raw or not side or delta is None or abs(delta) < max(SHOT_THRESHOLD, 0.01):
        return ""
    other = "home" if side == "away" else "away"
    opp, own = team_key(event[f"{other}_team"]), team_key(event[f"{side}_team"])
    if opp not in raw or own not in raw:
        return ""
    under = delta < 0
    def place(key, stat, most):
        v = raw[key][stat]
        return 1 + sum(1 for x in raw.values() if (x[stat] > v if most else x[stat] < v))
    out = []
    r = place(opp, "sf", under)  # under lean: opp shoots a lot? over lean: opp barely shoots?
    if r <= WARN_RANK:
        out.append(f"{ab[other]} {ordinal(r)} {'most' if under else 'least'} for")
    r = place(own, "sa", under)
    if r <= WARN_RANK:
        out.append(f"{ab[side]} {ordinal(r)} {'most' if under else 'least'} against")
    return ", ".join(out)


def rank_line(event, side, ab, raw, games=None):
    """Two lines, e.g.
        VGK L5 For: 32LAK, 43TOR, 28@SEA, 28@VAN, 30ANA (2nd most 33.0)
        LAK L4 Against: 32@VGK, 30FLA, 25@SJS, 29@COL (9th most 29.0)
    Ranks and averages use raw (unadjusted) season numbers, the ones you'd see looking a team up."""
    if not raw:
        return []
    other = "home" if side == "away" else "away"
    opp, own = team_key(event[f"{other}_team"]), team_key(event[f"{side}_team"])
    if opp not in raw or own not in raw:
        return []
    def place(key, stat):  # "7th most" for the top half, "4th least" for the bottom half
        val = raw[key][stat]
        most = 1 + sum(1 for t in raw.values() if t[stat] > val)
        least = 1 + sum(1 for t in raw.values() if t[stat] < val)
        return f"{ordinal(most)} most" if most <= least else f"{ordinal(least)} least"
    def line(team, key, stat, word):
        recent = recent_games(games, team, stat)
        head = ul(f"{team} L{len(recent)} {word}:") if recent else ul(f"{team} {word}:")
        body = (", ".join(recent) + " ") if recent else ""
        return f"{head} {body}({place(key, stat)} {raw[key][stat]:.1f})"
    return [line(ab[other], opp, "sf", "For"), line(ab[side], own, "sa", "Against")]


def book_parts(player, current, expected, delta, side=None, ctx=None):
    parts = []
    for book in BOOKS:
        ln = current.get(book, {}).get(player)
        short = BOOK_SHORT.get(book, book)
        if ln:
            parts.append(f"{short} {ln.get('point')}{target_tag(expected, ln.get('point'), delta, side, ctx, ln)}")
        else:
            parts.append(f"{short} not yet")
    return parts


def build_messages(event, new_pairs, current, m=None, sides=None, abbrevs=None, h2h=None,
                   known_before=(), show_h2h=True, raw=None, games=None, injuries=None,
                   state=None, now=None):
    """One message per goalie, so a reply of "in" always points at one goalie.
    Returns [(text, player, book or None)]; book is set for "added" one-liners.
    Goalies seen for the first time get a full block:
        Kuemper (LAK) - LAK@VGK 10:10PM
        DK 26.5 OVER · FD not yet
        30.9 shots, 27.3 saves expected
        H2H L4 VGK on LAK @25, 22, @27, 35 (avg 27.2)            <- once per game
        H2H L4 LAK on VGK 19, @33, 24, @26 (avg 25.5)
        VGK L5 For: 32LAK, 43TOR, 28@SEA, 28@VAN, 30ANA (2nd most 33.0)
        LAK L4 Against: 32@VGK, 30FLA, 25@SJS, 29@COL (9th most 29.0)
    A goalie already alerted who shows up at the other book gets one line:
        Kuemper (LAK) 26.5 OVER · 10:10PM (FD added)"""
    sides, abbrevs = sides or {}, abbrevs or {}
    ab = {s: abbrevs.get(team_key(event[f"{s}_team"])) or nickname(event[f"{s}_team"])
          for s in ("away", "home")}
    ctx = fire_context(event, ab, h2h, raw, m)
    new_goalies = sorted({p for _, p in new_pairs if p not in known_before})
    added = sorted((b, p) for b, p in new_pairs if p in known_before)
    msgs = []
    when = fmt_time(event['commence_time'])
    game = f"{ab['away']}@{ab['home']} {when}"
    for i, player in enumerate(new_goalies):
        out = []
        side = sides.get(player)
        g = m[side] if (m and side) else None
        expected, delta = (g["saves"], g["delta"]) if g else (None, None)
        label = f"{last_name(player)} ({ab[side]})" if side else last_name(player)
        out.append(f"{label} - {game}")
        out.append(" · ".join(book_parts(player, current, expected, delta, side, ctx)))
        if g:
            mk = matchup_marker(event, side, raw)
            warn = rank_warning(event, side, ab, raw, g["delta"])
            out.append(f"{g['shots']:.1f} shots, {g['saves']:.1f} saves expected"
                       + (f" · 🎯 {mk.lower()} matchup" if mk else "")
                       + (f" · ⚠️ {warn}" if warn else ""))
        elif m:
            out.append(f"Expected saves: {ab['away']} goalie {m['away']['saves']:.1f} / "
                       f"{ab['home']} goalie {m['home']['saves']:.1f} (team unknown)")
        if side:  # every goalie gets his own H2H line: shots on his team in recent meetings
            out.extend(fmt_h2h(h2h, ab, side))
        if side:
            out.extend(rank_line(event, side, ab, raw, games))
        if injuries:
            out.extend(injury_lines(injuries, ab, state, games, now))
        msgs.append(("\n".join(out), player, None))
    for book, player in added:
        side = sides.get(player)
        g = m[side] if (m and side) else None
        ln = current.get(book, {}).get(player, {})
        tag = target_tag(g["saves"] if g else None, ln.get("point"), g["delta"] if g else None, side, ctx, ln)
        who_ = (f"{last_name(player)} ({ab[side]})" if side
                else f"{last_name(player)} ({ab['away']}@{ab['home']})")
        reminder, better, mine = in_other_book(event["id"], player, BOOK_SHORT.get(book, book), ln.get("point"))
        code = tag_code(g["saves"] if g else None, ln.get("point"), g["delta"] if g else None)
        if mine and code in BET_SIDE and BET_SIDE[code] != mine and ln.get("point") is not None:
            # Owner Oct 28: you bet against the tag, so the tag's link opens the wrong side.
            # Add your side at this book, linked: '👉 You're in DK u27.5 · FD u27.5'
            reminder += " · " + link(f"{BOOK_SHORT.get(book, book)} {mine[0].lower()}{float(ln['point']):g}",
                                     ln.get(mine.lower() + "_link"))
        text = (f"{who_} {ln.get('point')}{tag}{' 🍀' if better else ''} · {when} "
                f"({BOOK_SHORT.get(book, book)} added)" + (f" {reminder}" if reminder else ""))
        msgs.append((text, player, book))
    return msgs


def in_other_book(event_id, player, book, point):
    """The second book posted a goalie you already bet at the first one. Returns
    ("👉 You're in DK u23.5", better, your side) where better = this book's number is better for your side
    (shown as 🍀 after the tag); (None, False, None) otherwise."""
    mine = [r for r in load_picks() if r["event_id"] == event_id and r["goalie"] == player and r.get("taken")]
    if not mine or any(r["book"] == book for r in mine):
        return None, False, None
    r = mine[0]
    side, taken = r["taken"], float(r["taken_line"])
    better = point is not None and ((side == "OVER" and float(point) < taken) or
                                    (side == "UNDER" and float(point) > taken))
    return f"👉 You're in {r['book']} {side[0].lower()}{taken:g}", better, side


def bet_effect(event_id, player, effect):
    """Injury alert line for your logged bet(s) on this goalie, e.g.
    '👉 You're in DK u23.5 (hurts your bet)'. effect = 'More'/'Fewer' shots on him. None if no bet."""
    seen, parts = set(), []
    for r in load_picks():
        if r["event_id"] != event_id or r["goalie"] != player or not r.get("taken"):
            continue
        play = f"{r['book']} {r['taken'][0].lower()}{float(r['taken_line']):g}"
        if play in seen:
            continue
        seen.add(play)
        helps = (r["taken"] == "OVER") == (effect == "More")
        parts.append(f"{play} ({'helps' if helps else 'hurts'} your bet)")
    return "👉 You're in " + " · ".join(parts) if parts else None


# ---------- injuries: key players only ----------
# Only a team's top shooters and top-minute defensemen count, so depth injuries never show up.
KEY_SHOOTERS = 3      # top shots-per-game skaters per team
KEY_DEFENSE = 2       # top ice-time defensemen per team
KEY_MIN_GP = 5        # games (this season + last, with this team) before a player can be "key"
SHOW_GTD = False      # owner: hide day-to-day players in alerts (Oct 12); True shows a GTD line
WITH_WITHOUT_MIN = 2  # show team shots with/without a key player once he's missed (and played) this many
INJURY_URL = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries"
INJURY_CONFIRM = timedelta(minutes=5)   # a new OUT must hold this long before an alert
INJURY_CLEAR = timedelta(minutes=30)    # off the list this long before he counts as back
INJURY_FEED_MIN = 30  # the league-wide list normally has ~100+ players; fewer means a bad fetch


def load_key_players(abbrev, now):
    """[{id, first, last, pos, sog, toi, role}] for a team's key players, from this season + last
    (games with this team only), limited to the current roster."""
    season = season_id(now)
    prev = f"{int(season[:4]) - 1}{season[:4]}"
    roster = nhl_get(f"{NHL_WEB}/roster/{abbrev}/current")
    on_roster = {p["id"] for grp in ("forwards", "defensemen") for p in roster.get(grp, [])}
    agg = {}
    for sid in (season, prev):
        try:
            skaters = nhl_get(f"{NHL_WEB}/club-stats/{abbrev}/{sid}/2").get("skaters", [])
        except Exception:
            skaters = []
        for p in skaters:
            if p["playerId"] not in on_roster:
                continue
            gp = p.get("gamesPlayed") or 0
            a = agg.setdefault(p["playerId"], {
                "id": p["playerId"], "first": p["firstName"]["default"], "last": p["lastName"]["default"],
                "pos": p.get("positionCode", ""), "gp": 0, "shots": 0, "toi": 0.0})
            a["gp"] += gp
            a["shots"] += p.get("shots") or 0
            a["toi"] += (p.get("avgTimeOnIcePerGame") or 0) * gp
    players = [a for a in agg.values() if a["gp"] >= KEY_MIN_GP]
    for a in players:
        a["sog"] = round(a["shots"] / a["gp"], 1)
        a["toi"] = round(a["toi"] / a["gp"] / 60, 1)  # minutes per game
    keys = {}
    for a in sorted(players, key=lambda a: -a["sog"])[:KEY_SHOOTERS]:
        keys[a["id"]] = dict(a, role="shooter")
    for a in sorted([a for a in players if a["pos"] == "D"], key=lambda a: -a["toi"])[:KEY_DEFENSE]:
        keys.setdefault(a["id"], dict(a, role="defense"))
    return list(keys.values())


POSITIONS = {"C": "C", "L": "LW", "R": "RW", "D": "D"}


def pos(k):
    return POSITIONS.get(k.get("pos", ""), k.get("pos", ""))


def name_match(first, last, ln, fn):
    return team_key(last) == team_key(ln) and (not fn or team_key(first)[:1] == team_key(fn)[:1])


def injury_report(state, events, abbrevs, now):
    """Key players currently on the injury list for every team playing in `events`.
    Returns ({abbrev: [player dict + status, new]}, [newly OUT players], [players back from OUT]).
    Free; runs every time."""
    teams = set(abbrevs.values())  # every team, so "NEW" really means it happened today
    keys = {t: cached(state, f"keys_{t}", now, timedelta(hours=12), lambda t=t: load_key_players(t, now)) or []
            for t in sorted(teams)}
    try:
        feed = nhl_get_any(INJURY_URL).get("injuries", [])
    except Exception as e:
        print(f"Couldn't load injuries ({e}); skipping them this run.")
        return {}, [], []
    if sum(len(t.get("injuries", [])) for t in feed) < INJURY_FEED_MIN:
        # A short/empty feed is almost surely a hiccup; don't treat everyone as healthy.
        print("Injury feed looks incomplete; skipping it this run.")
        return {}, [], []
    listed = {}
    for team in feed:
        ab = abbrevs.get(team_key(team.get("displayName", "")))
        for inj in team.get("injuries", []):
            ath = inj.get("athlete") or {}
            raw = (inj.get("status") or "").lower()
            status = "DTD" if ("day" in raw or raw in ("questionable", "probable")) else "OUT"
            listed.setdefault(ab, []).append((ath.get("firstName", ""), ath.get("lastName", ""), status))
    book = state.setdefault("injuries", {})       # "TEAM:id" -> {status, seen, out_at}
    seeded = set(state.setdefault("injury_teams", []))
    today = now.astimezone(LOCAL_TZ).date()
    report, newly_out, newly_back = {}, [], []
    for t in sorted(teams):
        first_look = t not in seeded
        current = {}
        for k in keys[t]:
            hit = next((st for fn, ln, st in listed.get(t, []) if name_match(k["first"], k["last"], ln, fn)), None)
            if hit:
                current[f"{t}:{k['id']}"] = (k, hit)
        # ESPN's feed is served by several caches that don't always agree, so a player can blink
        # off and back on between runs. Changes only count once they've held for a while.
        for kid, (k, st) in current.items():
            prev = book.get(kid)
            stamp = iso(now - timedelta(days=2)) if first_look else iso(now)
            if not prev:
                prev = book[kid] = {"status": st, "seen": stamp,
                                    "out_at": stamp if st == "OUT" else None,
                                    "alerted": first_look}  # first look at a team: nothing is news
            prev.pop("missing_since", None)
            if st != prev["status"]:
                if prev.get("pending") != st:
                    prev["pending"], prev["pending_since"] = st, iso(now)
                elif now - parse_iso(prev["pending_since"]) >= INJURY_CONFIRM:
                    prev.update(status=st)
                    if st == "OUT":
                        prev.update(out_at=iso(now), alerted=False)
                    prev.pop("pending", None); prev.pop("pending_since", None)
            else:
                prev.pop("pending", None); prev.pop("pending_since", None)
            if (prev["status"] == "OUT" and not prev.get("alerted", True)
                    and now - parse_iso(prev["out_at"] or prev["seen"]) >= INJURY_CONFIRM):
                prev["alerted"] = True  # one OUT alert per absence
                newly_out.append((t, k))
            new = any(x and parse_iso(x).astimezone(LOCAL_TZ).date() == today
                      for x in (prev["seen"], prev["out_at"]))
            report.setdefault(t, []).append(dict(k, status=prev["status"], new=new))
        for kid in [x for x in book if x.startswith(f"{t}:") and x not in current]:
            entry = book[kid]
            k = next((k for k in keys[t] if f"{t}:{k['id']}" == kid), None)
            missing = entry.setdefault("missing_since", iso(now))
            if now - parse_iso(missing) < INJURY_CLEAR:
                if k:  # probably a feed blip; keep treating him as injured for now
                    report.setdefault(t, []).append(dict(k, status=entry["status"], new=False))
                continue
            was = book.pop(kid)  # off the injury list long enough: back in the lineup
            if k and not first_look and (
                    (was.get("status") == "OUT" and was.get("alerted", True))
                    or was.get("status") == "DTD"):  # day-to-day player cleared (owner Oct 14, Makar)
                newly_back.append((t, dict(k, was=was.get("status"))))
        seeded.add(t)
    state["injury_teams"] = sorted(seeded)
    return report, newly_out, newly_back


def nhl_get_any(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (nhl-saves-alerts)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def played_dates(state, k, now):
    """Dates this season the player dressed (NHL game log, refreshed every 6 hours)."""
    def load():
        log = nhl_get(f"{NHL_WEB}/player/{k['id']}/game-log/{season_id(now)}/2").get("gameLog", [])
        return sorted({g.get("gameDate") for g in log if g.get("gameDate")})
    return set(cached(state, f"gl_{k['id']}", now, timedelta(hours=6), load) or [])


def games_missed(state, team, k, games, now):
    """Team games in a row he's missed so far (0 = tonight is the first). None if unknown."""
    if not games:
        return None
    played = played_dates(state, k, now)
    team_dates = sorted({d for d, a, h, *_ in games if team in (a, h)})
    last = max((d for d in team_dates if d in played), default=None)
    return sum(1 for d in team_dates if last is None or d > last)


def with_without(state, team, k, games, now):
    """Team shots with and without a player this season: (with_avg, n_with, without_avg, n_without)."""
    played = played_dates(state, k, now)
    stat_with, stat_without = [], []
    for d, a, h, asog, hsog in games or []:
        if team not in (a, h):
            continue
        away = team == a
        val = (asog if away else hsog) if k["role"] == "shooter" else (hsog if away else asog)
        (stat_with if d in played else stat_without).append(val)
    if len(stat_with) < WITH_WITHOUT_MIN or len(stat_without) < WITH_WITHOUT_MIN:
        return None
    return (sum(stat_with) / len(stat_with), len(stat_with),
            sum(stat_without) / len(stat_without), len(stat_without))


def injury_lines(report, ab, state=None, games=None, now=None):
    """One line per key player missing, nothing when nobody key is:
        INJ: Faber D (MIN) 25 min NEW                     <- out; tonight is his first game missed
        INJ: Marchand LW (FLA) 2.6 SOG/g (3) · SF w/ 30.5 (2), w/o 25.3 (3)   <- out, missed 3 so far
        GTD: Ekholm D (EDM) 22 min                        <- day-to-day, may still play"""
    lines = []
    live = state is not None and now is not None
    for t in (ab["away"], ab["home"]):
        for k in report.get(t, []):
            what = f"{k['sog']} SOG/g" if k["role"] == "shooter" else f"{k['toi']:.0f} min"
            if k["status"] == "OUT":
                missed = games_missed(state, t, k, games, now) if live else None
                tag = ("NEW" if k["new"] else "") if missed is None else ("NEW" if missed == 0 else f"({missed})")
                line = f"{ul('INJ:')} {k['last']} {pos(k)} ({t}) {what}" + (f" {tag}" if tag else "")
            elif SHOW_GTD:
                line = f"{ul('GTD:')} {k['last']} {pos(k)} ({t}) {what}"
            else:
                continue  # day-to-day hidden; a change alert comes if he's ruled out
            ww = with_without(state, t, k, games, now) if live else None
            if ww:
                stat = "SF" if k["role"] == "shooter" else "SA"
                line += f" · {stat} w/ {ww[0]:.1f} ({ww[1]}), w/o {ww[2]:.1f} ({ww[3]})"
            lines.append(line)
    return lines


def send_injury_change(state, events, stats, abbrevs, team, k, now, back=False):
    """'⚠️ Sanderson D (OTT) OUT - OTT@NJD 7:10PM' + which already-alerted goalie it affects.
    Only for games today that haven't started and that you've already had an alert for."""
    today = now.astimezone(LOCAL_TZ).date()
    for event in events:
        start = parse_iso(event["commence_time"])
        if start <= now or start.astimezone(LOCAL_TZ).date() != today:
            continue
        ab = {s: abbrevs.get(team_key(event[f"{s}_team"])) for s in ("away", "home")}
        if team not in ab.values():
            continue
        rec = state["events"].get(event["id"], {})
        posted = {p for players in rec.get("lines", {}).values() for p in players}
        if not posted:
            continue  # no alert yet; the injury will show in the alert when it comes
        team_side = "away" if ab["away"] == team else "home"
        other = "home" if team_side == "away" else "away"
        # A missing shooter means fewer shots on the other goalie; a missing D means more on his own.
        # A player coming back flips it.
        hit_side, effect = (other, "Fewer") if k["role"] == "shooter" else (team_side, "More")
        if back:
            effect = "More" if effect == "Fewer" else "Fewer"
        m = matchup(event, stats)
        sides = goalie_sides(event, posted, state, now) if m else {}
        head = (f"⚠️ {k['last']} {pos(k)} ({team}) OUT" if not back else
                f"✅ {k['last']} {pos(k)} ({team}) CLEARED (off day-to-day)" if k.get("was") == "DTD" else
                f"✅ {k['last']} {pos(k)} ({team}) BACK")
        lines = [f"{head} - {ab['away']}@{ab['home']} {fmt_time(event['commence_time'])}"]
        for player in sorted(p for p in posted if sides.get(p) == hit_side):
            g = m[hit_side]
            lines.append(f"{effect} shots on {last_name(player)} ({ab[hit_side]}): "
                         + " · ".join(book_parts(player, rec["lines"], g["saves"], g["delta"], hit_side)))
            mine = bet_effect(event["id"], player, effect)
            if mine:
                lines.append(mine)
        if len(lines) == 1:
            lines.append(f"{effect} shots expected on the {ab[hit_side]} goalie")
        send_push("", "\n".join(lines))
        print(f"INJURY ALERT {k['last']} ({team}) {'BACK' if back else 'OUT'}")


def key_out_summary(report, ab):
    """For the pick log: 'WSH:Ovechkin,Carlson(DTD);NYR:'."""
    return ";".join(f"{t}:" + ",".join(k["last"] + ("(DTD)" if k["status"] == "DTD" else "")
                                       for k in report.get(t, []))
                    for t in (ab["away"], ab["home"]))


# ---------- your bets: reply "in" to an alert ----------

def tg_call(method, params):
    """Telegram Bot API call that never stops the run; returns the result or None."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return None
    req = urllib.request.Request(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}",
                                 data=urllib.parse.urlencode(params).encode("utf-8"))
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("result") if data.get("ok") else None
    except Exception as e:
        print(f"Telegram {method} failed: {e}")
        return None


def tg_reply(msg, text):
    tg_call("sendMessage", {"chat_id": TELEGRAM_CHAT_ID, "text": text,
                            "reply_to_message_id": msg["message_id"],
                            "disable_notification": "true"})


def tg_react(msg, emoji="👍", fallback="Logged ✅"):
    ok = tg_call("setMessageReaction", {"chat_id": TELEGRAM_CHAT_ID, "message_id": msg["message_id"],
                                        "reaction": json.dumps([{"type": "emoji", "emoji": emoji}])})
    if ok is None:  # reactions unavailable: fall back to a short text
        tg_reply(msg, fallback)


def grade_taken(r):
    """Score a bet you logged, against the line you took."""
    if not r.get("taken"):
        return
    if r.get("outcome") == "VOID":
        r["taken_result"] = "VOID"
        return
    if r.get("actual_saves") in (None, ""):
        return
    saves, line = float(r["actual_saves"]), float(r["taken_line"])
    r["taken_result"] = ("P" if saves == line else
                         "W" if (saves > line) == (r["taken"] == "OVER") else "L")


PAST_BETS_FILE = os.path.join(HERE, "past_bets.csv")  # bets from before the bot logged them (Claude-edited)


def past_bets():
    """Straight saves bets the bot couldn't log: DK slips from before logging started (Sep 30 -
    Oct 8) plus later bets on goalies that were never alerted (e.g. Hellebuyck Oct 27), as
    pick-log-like rows so they count in "Your season". One goalie per game."""
    try:
        with open(PAST_BETS_FILE, newline="") as f:
            return [{"event_id": f"past:{r['date']}:{r['game']}", "goalie": r["goalie"],
                     "taken": r["side"], "taken_line": r["line"], "taken_result": r["result"],
                     "taken_at": r["date"], "date": r["date"]} for r in csv.DictReader(f)]
    except FileNotFoundError:
        return []


def my_record(rows):
    """Your record, counting each goalie once per game (the first bet you logged on him),
    so it measures how often your reads are right. Returns (w, l, p, bets) where bets is
    the number of graded bets behind it, including second-book bets on the same goalie."""
    graded = sorted((r for r in rows if r.get("taken_result") in ("W", "L", "P")),
                    key=lambda r: r.get("taken_at", ""))
    first = {}
    for r in graded:
        first.setdefault((r["event_id"], r["goalie"]), r)
    res = [r["taken_result"] for r in first.values()]
    return res.count("W"), res.count("L"), res.count("P"), len(graded)



# Owner Oct 28: "I'm taking 27u" / "Taking the 27u under" were ignored. Accepted openers:
# in, took, taking, take, each optionally after I / I'm / Im / I am (straight or curly apostrophe).
BET_START = r"(?:i\s+am\s+|i['\u2019]?m\s+|i\s+)?(?:in|took|taking|take)\b"


BET_TOKEN = re.compile(r"^(?:([ou])(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)([ou])?)$")


def parse_bet(words):
    """One bet: 'jarry 23u', 'u24 fd', 'o', '24.5', 'dk' ... -> {name, side, line, book}.
    A whole number means the half-point line bettors shorthand it for: 23 -> 23.5."""
    bet = {"book": None, "side": None, "line": None, "name": None}
    for w in words:
        w = w.strip(".,!?;:")
        if not w:
            continue
        m = BET_TOKEN.match(w)
        if w in ("dk", "draftkings"):
            bet["book"] = "DK"
        elif w in ("fd", "fanduel"):
            bet["book"] = "FD"
        elif w in ("o", "over"):
            bet["side"] = "OVER"
        elif w in ("u", "under"):
            bet["side"] = "UNDER"
        elif m:
            side = m.group(1) or m.group(4)
            num = m.group(2) or m.group(3)
            if side:
                bet["side"] = "OVER" if side == "o" else "UNDER"
            line = float(num)
            bet["line"] = line + 0.5 if line == int(line) else line
        elif w not in ("and", "the", "at", "on", "for", "i", "took", "in", "taking", "take",
                       "i'm", "i\u2019m", "im", "am"):
            bet["name"] = w
    return bet


def parse_message(text):
    """Split a typed message into bets. Returns (command, [bet, ...]) or (None, []).
    Understands 'in ...', 'took ...', 'I took ...', 'out ...', with bets separated by commas,
    new lines or 'and': 'I took Jarry 23u, Fowler 22o, Ellis 23 and 25o'."""
    t = text.lower().strip()
    m = re.match(r"^(?:i\s+am\s+|i['\u2019]?m\s+|i\s+)?(in|took|taking|take|out)\b[\s.!:,-]*(.*)$", t, re.S)
    if not m:
        return None, []
    cmd = "out" if m.group(1) == "out" else "in"
    chunks = [c.split() for c in re.split(r",|\n|;|\band\b|&", m.group(2))]
    bets = [parse_bet(c) for c in chunks if c] or [parse_bet([])]
    for i, b in enumerate(bets):  # 'Ellis 23 and 25o': carry the name forward, share the side
        if not b["name"] and i:
            b["name"] = bets[i - 1]["name"]
    for b in bets:
        if not b["side"]:
            same = {x["side"] for x in bets if x["name"] == b["name"] and x["side"]}
            if len(same) == 1:
                b["side"] = same.pop()
    return cmd, bets


BET_WORDS = {"i", "in", "took", "taking", "take", "i'm", "i\u2019m", "im", "am", "for", "at", "on", "the", "dk", "fd", "draftkings", "fanduel",
             "o", "u", "over", "under"}


def split_bet_note(text, is_reply):
    """Owner Oct 16: he adds his reasoning after the bet without typing 'note'.
    Swipe reply ('in for 26o. h2h history looks good'): the bet ends at the first word that
    isn't part of a bet; the rest is a note. Typed bets ('I took Wally 26o. VGK weak at home'):
    the first sentence is the bet, the rest a note. Returns (bet_text, note or None)."""
    if not re.match(r"^\s*" + BET_START, text, re.I):
        return text, None
    if is_reply:
        for m in re.finditer(r"\S+", text):
            w = m.group().strip(".,!?;:").lower()
            if w and w not in BET_WORDS and not BET_TOKEN.match(w):
                note = text[m.start():].strip()
                return text[:m.start()], note or None
        return text, None
    m = re.search(r"[.!?]\s+(?=\S)", text)
    if m and len(text[m.end():].split()) >= 2:
        return text[:m.start()], text[m.end():].strip()
    return text, None


def apply_bet(rows, state, event_id, goalie, alert_book, bet, cmd, now):
    """Mark one picks.csv row as your bet. Returns (ok, text describing it or the problem)."""
    mine = [r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie]
    name = last_name(goalie)
    if not mine:
        return False, f"Couldn't find {name} in the pick log."
    if cmd == "out":
        for r in mine:
            r.update(taken="", taken_line="", taken_result="", taken_at="")
        return True, f"{name} removed"
    book = bet["book"] or alert_book
    pool = [r for r in mine if r["book"] == book] if book else mine
    if not pool:
        return False, f"{book} hasn't posted {name}, so I can't log that one."
    side = bet["side"]
    if not side:
        sides = {BET_SIDE.get(r["tag"]) for r in pool}
        if len(sides) != 1 or None in sides:
            return False, f"No direction on {name} (NO EDGE). Add o or u, like: in {name} o{pool[0]['line']}"
        side = sides.pop()
    rec = state["events"].get(event_id, {})
    def lines_of(r):  # line logged with the alert and the newest seen for that book
        out = {float(r["line"])}
        for full, short in BOOK_SHORT.items():
            if short == r["book"]:
                pt = rec.get("lines", {}).get(full, {}).get(goalie, {}).get("point")
                if pt is not None:
                    out.add(float(pt))
        return out
    if bet["line"] is not None:  # the book whose line matches what you took
        line = bet["line"]
        row = min(pool, key=lambda r: min(abs(x - line) for x in lines_of(r)))
    else:  # best number for your side across the books shown, using the newest line
        def newest(r):
            return float(r["line"]) if len(lines_of(r)) == 1 else max(lines_of(r) - {float(r["line"])})
        row = (min if side == "OVER" else max)(pool, key=newest)
        line = newest(row)
    row.update(taken=side, taken_line=f"{line:g}", taken_at=iso(now))
    grade_taken(row)  # in case the game is already graded
    return True, f"{name} {side[0].lower()}{line:g} {row['book']}"


NICKNAMES_FILE = os.path.join(HERE, "nicknames.csv")  # your nicknames: goalie,nickname (e.g. Wallstedt,Wally)


def load_nicknames():
    """{'wally': {'wallstedt'}, 'hilly': {'hildeby', 'hill'}, ...} from nicknames.csv.
    A nickname can point at more than one goalie; the one alerted most recently wins."""
    out = {}
    try:
        with open(NICKNAMES_FILE, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("nickname") and r.get("goalie"):
                    out.setdefault(team_key(r["nickname"]), set()).add(team_key(r["goalie"]))
    except FileNotFoundError:
        pass
    return out


def find_by_name(rows, name, now):
    """Most recent alerted goalie whose last name (or one of your nicknames for him) matches
    `name`, from the last two days."""
    since = (now.astimezone(LOCAL_TZ) - timedelta(days=2)).strftime("%Y-%m-%d")
    key = team_key(name)
    if not key:
        return None
    keys = {key} | load_nicknames().get(key, set())  # the name itself still counts (e.g. "Murray")
    hits = [r for r in rows if r["date"] >= since
            and any(team_key(last_name(r["goalie"])).startswith(k) for k in keys)]
    if not hits:
        return None
    best = max(hits, key=lambda r: (r["date"], r.get("logged_at", "")))
    return best["event_id"], best["goalie"]


def process_replies(state, now):
    """Read your messages to the bot. Swipe left on an alert and reply "in", or type
    "I took Jarry 23u, Fowler 22o". Each run reads new messages once."""
    updates = tg_call("getUpdates", {"offset": state.get("tg_offset", 0), "timeout": 0,
                                     "allowed_updates": json.dumps(["message", "my_chat_member"])})
    resends = []  # handled later in the run, once stats and injuries are loaded
    if not updates:
        return resends, []
    manual = []
    rows, changed = None, False
    for u in updates:
        state["tg_offset"] = u["update_id"] + 1
        if u.get("my_chat_member"):
            channel_membership(state, u["my_chat_member"])
            continue
        msg = u.get("message") or {}
        if str((msg.get("chat") or {}).get("id")) != str(TELEGRAM_CHAT_ID):
            continue
        words = (msg.get("text") or "").lower().split()
        if words and words[0].strip(".!") in ("resend", "show"):
            resends.append((msg, (msg.get("text") or "").split()[1:]))  # names as you typed them
            continue
        if words and words[0].strip(".!:") == "line":
            manual.append((msg, (msg.get("text") or "").split()[1:]))
            continue
        low = " ".join(w.strip(".!?") for w in words)
        if low in ("pause channel", "channel off", "channel pause", "mute channel", "stop channel"):
            state["channel_paused"] = True
            tg_reply(msg, "📣 Channel paused. Your bets won't be posted until you text: resume channel. "
                          "Plays already posted still get their results.")
            continue
        if low in ("resume channel", "channel on", "channel resume", "unmute channel", "start channel"):
            state.pop("channel_paused", None)
            tg_reply(msg, "📣 Channel back on. Bets you log before puck drop will post again.")
            continue
        if words and words[0].strip(".!:?") in ("watch", "unwatch", "watching"):
            rows = rows if rows is not None else load_picks()
            target = state["sent"].get(str((msg.get("reply_to_message") or {}).get("message_id")))
            watch_command(msg, words, rows, state, target, now)
            continue
        if words and words[0].strip(".!:?") in SUMMARY_WORDS:
            rows = rows if rows is not None else load_picks()
            tg_reply(msg, plays_summary(rows, state, now, yesterday="yesterday" in words[1:]))
            continue
        if words and words[0].strip(".!:") in ("note", "notes"):
            rows = rows if rows is not None else load_picks()
            target = state["sent"].get(str((msg.get("reply_to_message") or {}).get("message_id")))
            save_note(msg, rows, target, now)
            continue
        text = msg.get("text") or ""
        # "In for 24o. Note COL shoots a lot" -> the bet, plus a note on the same goalie
        both = re.match(r"^(\s*" + BET_START + r".*?)[\s.;,!-]+notes?\b[:\s]*(.+)$", text, re.I | re.S)
        note_text = None
        if both:
            text, note_text = both.group(1), both.group(2).strip()
        else:  # "in for 26o. h2h looks good and BOS shooting" -> the bet, plus the rest as a note
            text, note_text = split_bet_note(text, bool((msg.get("reply_to_message") or {}).get("message_id")))
        cmd, bets = parse_message(text)
        if not cmd:
            # Owner Oct 28: never stay silent. A message the bot can't read gets a short hint.
            if (msg.get("text") or "").strip():
                tg_reply(msg, "🤔 Didn't catch that, nothing logged. Start with in / took / taking, "
                              "e.g. in 27u (swipe-reply) or took Woll 27u. Notes: note Woll ...")
            continue
        rows = rows if rows is not None else load_picks()
        target = state["sent"].get(str((msg.get("reply_to_message") or {}).get("message_id")))
        done, problems = [], []
        noted_for = None
        for bet in (bets[:1] if target else bets):
            if target:
                event_id, goalie, alert_book = target["event_id"], target["goalie"], target.get("book")
            else:
                found = find_by_name(rows, bet["name"], now) if bet["name"] else None
                if not found:
                    problems.append(f"Couldn't find {bet['name']} in the last two days of alerts."
                                    if bet["name"] else
                                    "Swipe left on an alert and reply in, or type: I took Kuemper 26o")
                    continue
                (event_id, goalie), alert_book = found, None
            noted_for = noted_for or {"event_id": event_id, "goalie": goalie}
            ok, note = apply_bet(rows, state, event_id, goalie, alert_book, bet, cmd, now)
            (done if ok else problems).append(note)
            changed = changed or ok
        if note_text:
            if noted_for or target:
                save_note({"text": "note " + note_text}, rows, noted_for or target, now, quiet=True)
                done_note = "Noted ✍"
            else:
                done_note = None
        if target and done and not problems and not note_text:
            tg_react(msg, "👍" if cmd == "in" else "👌")
        elif done or problems:
            tg_reply(msg, ("Logged: " + " · ".join(done) if done else "")
                     + (f" · {done_note}" if note_text and done_note else "")
                     + ("\n" if done and problems else "") + "\n".join(problems))
    if changed:
        save_picks(rows)
        try:
            channel_sync(state, rows, now)
        except Exception as e:
            print(f"Picks channel update skipped ({e}).")
    return resends, manual


SUMMARY_WORDS = ("summarize", "summarise", "summary", "plays", "recap", "today")


def plays_summary(rows, state, now, yesterday=False):
    """'summarize' (or 'summary', 'plays', 'recap'; add 'yesterday' for last night): every bet
    you've logged for today's games, one line per goalie in puck-drop order: 'Gibson (DET) - o24.5'.
    Just the plays (no tags, books or times); results once graded. Free (no odds call)."""
    day = now.astimezone(LOCAL_TZ) - timedelta(days=1 if yesterday else 0)
    date = day.strftime("%Y-%m-%d")
    mine = [r for r in rows if r["date"] == date and r.get("taken")]
    when = "yesterday" if yesterday else "today"
    if not mine:
        return f"No plays logged {when} ({day.strftime('%a %b %-d')})."
    marks = {"W": " ✅", "L": " ❌", "P": " push", "VOID": " void"}
    lines, done = [], []
    for r in sorted(mine, key=lambda r: (r.get("commence_time", ""), r["goalie"], r.get("taken_at", ""))):
        gkey = (r["event_id"], r["goalie"])
        if gkey in done:
            continue
        done.append(gkey)
        bets = sorted((x for x in mine if (x["event_id"], x["goalie"]) == gkey), key=lambda x: x.get("taken_at", ""))
        parts = [f"{x['taken'][0].lower()}{x['taken_line']}" + marks.get(x.get("taken_result"), "") for x in bets]
        saves = f": {r['actual_saves']} saves" if r.get("actual_saves") not in (None, "") else ""
        team = f" ({r['team']})" if r.get("team") else ""
        lines.append(f"{last_name(r['goalie'])}{team} - " + " · ".join(parts) + saves)
    head = f"📋 Your plays {when} ({day.strftime('%a %b %-d')})"
    foot = (f"{len(done)} goalie{'s' * (len(done) != 1)}"
            + (f", {len(mine)} bets" if len(mine) != len(done) else ""))
    if any(x.get("taken_result") in ("W", "L", "P") for x in mine):
        w, l, p, _ = my_record(mine)
        foot += " · " + fmt_record(w, l, p)
    return head + "\n" + "\n".join(lines) + "\n" + foot


# ---------- picks channel (owner Oct 18): your plays, posted for friends ----------
# A private Telegram channel you own, with this bot as an admin. Only you (via the bot) post;
# no comments unless you link a discussion group; reactions are a channel setting.

def channel_membership(state, upd):
    """You added (or removed) the bot as an admin of a channel: remember it as the picks channel."""
    chat, who = upd.get("chat") or {}, upd.get("from") or {}
    if chat.get("type") != "channel" or str(who.get("id")) != str(TELEGRAM_CHAT_ID):
        return  # only channels, and only when you're the one who added the bot
    status = (upd.get("new_chat_member") or {}).get("status")
    title = chat.get("title") or "your channel"
    if status == "administrator":
        state["picks_channel"] = {"id": chat["id"], "title": title}
        send_push("", f"📣 Picks channel connected: {title}. From now on, when you log a bet "
                      f"with in before puck drop, I'll post the play there, then the result.")
    elif status in ("left", "kicked", "member") and (state.get("picks_channel") or {}).get("id") == chat.get("id"):
        state.pop("picks_channel", None)
        send_push("", f"📣 Picks channel disconnected ({title}). Nothing will be posted there.")


def channel_lines(rows, state, event_id, goalie):
    """Your side on each book, as posted now: ({'DK': 23.5, 'FD': 24.5}, side, first bet row).
    A book that hasn't posted him is left out."""
    bets = sorted((r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie and r.get("taken")),
                  key=lambda r: r.get("taken_at", ""))
    if not bets:
        return {}, None, None
    first = bets[0]
    rec = state["events"].get(event_id, {})
    lines = {}
    for full, short in BOOK_SHORT.items():
        ln = rec.get("lines", {}).get(full, {}).get(goalie)
        if ln and ln.get("point") is not None:
            lines[short] = {"point": ln["point"], "url": ln.get(first["taken"].lower() + "_link")}
    if first["book"] not in lines:  # the line you took, if the feed lost it
        lines[first["book"]] = {"point": float(first["taken_line"]), "url": None}
    return lines, first["taken"], first


def channel_book_parts(lines, side):
    """'DK u23.5 · FD not yet', each posted line linked to that book's slip for your side."""
    s = side[0].lower()
    parts = []
    for b in BOOK_SHORT.values():
        if b in lines:
            play = f"{s}{float(lines[b]['point']):g}"
            parts.append(f"{b} {link(play, lines[b].get('url'))}")
        else:
            parts.append(f"{b} not yet")
    return " · ".join(parts)


def channel_post_text(state, first, goalie, lines, side):
    abbrevs = (state.get("team_abbrevs") or {}).get("value") or {}
    away = abbrevs.get(team_key(first["away_team"])) or nickname(first["away_team"])
    home = abbrevs.get(team_key(first["home_team"])) or nickname(first["home_team"])
    name = f"{last_name(goalie)} ({first['team']})" if first.get("team") else last_name(goalie)
    return (f"{name} - {away}@{home} {fmt_time(first['commence_time'])}\n"
            + channel_book_parts(lines, side))


def channel_sync(state, rows, now):
    """After you log bets: post each new goalie's play to the picks channel (once per goalie per
    game, only before puck drop), with both books: 'DK u23.5 · FD not yet' (owner Oct 18).
    'out' before puck drop takes the post down."""
    ch = state.get("picks_channel")
    if not ch:
        return
    posts = state.setdefault("channel_posts", {})
    paused = state.get("channel_paused")  # 'pause channel': no new posts; outs and results still work
    taken = {(r["event_id"], r["goalie"]) for r in rows if r.get("taken") and r.get("commence_time")
             and parse_iso(r["commence_time"]) > now}
    for event_id, goalie in sorted(taken):
        key = f"{event_id}|{goalie}"
        if key in posts:
            continue
        if paused:  # logged while paused: never posted, even after you resume
            start = next(r["commence_time"] for r in rows if r["event_id"] == event_id)
            posts[key] = {"mid": None, "skipped": True, "done": True, "start": start}
            continue
        lines, side, first = channel_lines(rows, state, event_id, goalie)
        if not first:
            continue
        text = channel_post_text(state, first, goalie, lines, side)
        mid = send_push("", text, chat_id=ch["id"])
        if mid:
            posts[key] = {"mid": mid, "side": side, "start": first["commence_time"], "text": text,
                          "lines": {b: v["point"] for b, v in lines.items()}}
    for key, post in list(posts.items()):
        event_id, goalie = key.split("|", 1)
        if post.get("mid") and parse_iso(post["start"]) > now and not any(
                r["event_id"] == event_id and r["goalie"] == goalie and r.get("taken") for r in rows):
            tg_call("deleteMessage", {"chat_id": ch["id"], "message_id": post["mid"]})  # you took it back
            posts.pop(key)
    cutoff = iso(now - timedelta(days=3))
    state["channel_posts"] = {k: v for k, v in posts.items() if v["start"] > cutoff}


def channel_added(state, event_id, goalie, book, now):
    """The other book just posted a goalie you're in on: fill in the channel post and ping:
    'Markstrom (FLA) u24.5 now on FD' (owner Oct 18). Before puck drop only."""
    ch = state.get("picks_channel")
    post = (state.get("channel_posts") or {}).get(f"{event_id}|{goalie}")
    short = BOOK_SHORT.get(book, book)
    if not (ch and post and post.get("mid")) or short in post["lines"] or parse_iso(post["start"]) <= now:
        return
    rows = load_picks()
    lines, side, first = channel_lines(rows, state, event_id, goalie)
    if short not in lines:
        return
    text = channel_post_text(state, first, goalie, lines, side)
    tg_call("editMessageText", {"chat_id": ch["id"], "message_id": post["mid"],
                                "text": to_html(text), "parse_mode": "HTML",
                                "disable_web_page_preview": "true"})
    name = f"{last_name(goalie)} ({first['team']})" if first.get("team") else last_name(goalie)
    play = f"{side[0].lower()}{float(lines[short]['point']):g}"
    send_push("", f"{name} {link(play, lines[short].get('url'))} now on {short}",
              chat_id=ch["id"], reply_to=post["mid"])
    post["lines"] = {b: v["point"] for b, v in lines.items()}
    post["text"] = text


def channel_result(state, rows, event_id, goalie, correction_from=None):
    """Reply to the play's post with the result at each book posted:
    '✅ Markstrom (FLA) DK u23.5 · FD u24.5: 20 saves' (mixed: 'DK u23.5 ✅ · FD u22.5 ❌')."""
    ch, post = state.get("picks_channel"), (state.get("channel_posts") or {}).get(f"{event_id}|{goalie}")
    if not (ch and post and post.get("mid")):
        return
    bets = sorted((r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie and r.get("taken")),
                  key=lambda r: r.get("taken_at", ""))
    if not bets:
        return
    r = bets[0]
    name = f"{last_name(goalie)} ({r['team']})" if r.get("team") else last_name(goalie)
    side = post.get("side") or r["taken"]
    s = side[0].lower()
    if r.get("taken_result") == "VOID" or r.get("actual_saves") in (None, ""):
        text = f"{name}: didn't play (void)"
    else:
        saves = float(r["actual_saves"])
        res = {}
        for b, pt in (post.get("lines") or {r["book"]: float(r["taken_line"])}).items():
            pt = float(pt)
            res[b] = "P" if saves == pt else ("W" if (saves > pt) == (side == "OVER") else "L")
        plays = [f"{b} {s}{float(pt):g}" for b, pt in (post.get("lines") or {}).items()] or [f"{r['book']} {s}{r['taken_line']}"]
        marks = list(res.values())
        if len(set(marks)) == 1:
            text = f"{MARKS.get(marks[0], '')} {name} " + " · ".join(plays) + f": {r['actual_saves']} saves"
        else:
            text = (f"{name} " + " · ".join(f"{p} {MARKS.get(x, '')}" for p, x in zip(plays, marks))
                    + f": {r['actual_saves']} saves")
    if correction_from is not None:
        text = f"🔁 Stat correction: {text} (was {correction_from})"
    send_push("", text, chat_id=ch["id"], reply_to=post["mid"])
    post["done"] = True


def channel_catchup(state):
    """Post the result for every channel play that's been graded (live or in the morning)."""
    posts = state.get("channel_posts") or {}
    if not (state.get("picks_channel") and any(not p.get("done") for p in posts.values())):
        return
    rows = load_picks()
    for key, post in posts.items():
        if post.get("done"):
            continue
        event_id, goalie = key.split("|", 1)
        first = min((r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie and r.get("taken")),
                    key=lambda r: r.get("taken_at", ""), default=None)
        if first and first.get("taken_result") in ("W", "L", "P", "VOID"):
            channel_result(state, rows, event_id, goalie)


def save_note(msg, rows, target, now, quiet=False):
    """'note Wallstedt faded, VGK low H2H, MIN tight at home' (or swipe-reply 'note ...' on an alert).
    Saved to notes.csv with the goalie's line/tag/expected at the time, for the daily review."""
    text = (msg.get("text") or "").split(None, 1)
    body = text[1].strip() if len(text) > 1 else ""
    if not body:
        tg_reply(msg, "Add your note after the word note, like: note Wallstedt faded, VGK low H2H")
        return
    found = None
    if target:
        found = (target["event_id"], target["goalie"])
    else:  # first word may be a goalie's last name from the last two days of alerts
        first = body.split()[0].strip(",.:")
        found = find_by_name(rows, first, now) if first else None
        if found:
            body = body[len(body.split()[0]):].strip(" ,.:-") or body
    row = next((r for r in rows if found and (r["event_id"], r["goalie"]) == found), None)
    note = {"noted_at": iso(now), "note": body,
            "date": row["date"] if row else now.astimezone(LOCAL_TZ).strftime("%Y-%m-%d"),
            "goalie": row["goalie"] if row else "", "team": row.get("team", "") if row else "",
            "game": row["game"] if row else "", "tag": row["tag"] if row else "",
            "line": row["line"] if row else "", "expected_saves": row["expected_saves"] if row else "",
            "event_id": row["event_id"] if row else ""}
    new_file = not os.path.exists(NOTES_FILE)
    with open(NOTES_FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=NOTE_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(note)
    if quiet:
        return note
    if target:
        tg_react(msg, "✍", "Noted ✍")
    else:
        tg_reply(msg, f"Noted{' for ' + last_name(note['goalie']) if note['goalie'] else ''} ✍")
    return note


def alert_new_lines(event, rec, new_pairs, known_before, m, stats, state, injuries, now):
    """Send the alert(s) for newly posted (book, goalie) lines and log them as picks."""
    sides = goalie_sides(event, {p for _, p in new_pairs}, state, now) if m else {}
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    h2h = get_h2h(state, abbrevs.get(team_key(event["away_team"])),
                  abbrevs.get(team_key(event["home_team"])), now)
    show_h2h = not rec.get("h2h_sent")
    for text, player, book in build_messages(
            event, new_pairs, rec["lines"], m, sides, abbrevs, h2h, known_before, show_h2h,
            (stats or {}).get("raw"), (state.get("game_log") or {}).get("games"),
            injuries, state, now):
        mid = send_push("", text)
        if mid:
            state["sent"][str(mid)] = {"event_id": event["id"], "goalie": player,
                                       "book": BOOK_SHORT.get(book, book) if book else None,
                                       "at": iso(now)}
    if show_h2h and h2h and any(p not in known_before for _, p in new_pairs):
        rec["h2h_sent"] = True
    log_picks(event, new_pairs, rec["lines"], m, sides, abbrevs, now, h2h, (stats or {}).get("raw"),
              injuries, stats)
    names = ", ".join(f"{p} ({BOOK_SHORT.get(b, b)})" for b, p in sorted(new_pairs))
    print(f"ALERT {rec['matchup']}: {names}")
    for book, player in sorted(new_pairs):  # the other book posted a goalie you're in on
        try:
            channel_added(state, event["id"], player, book, now)
        except Exception as e:
            print(f"Picks channel update skipped ({e}).")


def ascii_name(name):
    return unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()


# ---------- line-move watch (owner Oct 27: "DeSmith 25u looks like it's bleeding up") ----------
WATCH_MINUTES = 5        # how often a watched goalie's game is checked (1 credit per check)
WATCH_PRICE_MOVE = 0.03  # also ping when the price on your side moves this much (implied %), e.g. -115 -> -130


def implied(price):
    return None if price is None else (-price / (-price + 100) if price < 0 else 100 / (price + 100))


def watch_command(msg, words, rows, state, target, now):
    """'watch desmith 25u' / swipe-reply 'watch' on an alert: ping when his line or the price on
    your side moves before puck drop. 'unwatch desmith', 'watching' lists them."""
    w = state.setdefault("watch", {})
    cmd = words[0].strip(".!:?")
    if cmd == "watching":
        live = [k.split("|", 1)[1] for k, v in w.items() if parse_iso(v["start"]) > now]
        tg_reply(msg, "👀 Watching: " + ", ".join(last_name(g) for g in live) if live else "Not watching any lines.")
        return
    rest = [x for x in words[1:]]
    bet = parse_bet(rest)
    found = ((target["event_id"], target["goalie"]) if target else
             (find_by_name(rows, bet["name"], now) if bet["name"] else None))
    if not found:
        tg_reply(msg, "Which goalie? Like: watch desmith 25u (or swipe-reply watch on his alert)")
        return
    event_id, goalie = found
    key = f"{event_id}|{goalie}"
    if cmd == "unwatch":
        w.pop(key, None)
        tg_reply(msg, f"👀 Stopped watching {last_name(goalie)}.")
        return
    rec = state["events"].get(event_id)
    if not rec or parse_iso(rec["commence_time"]) <= now:
        tg_reply(msg, f"{last_name(goalie)}'s game has started or isn't in the feed.")
        return
    mine = [r for r in rows if r["event_id"] == event_id and r["goalie"] == goalie]
    side = bet["side"] or next((r["taken"] for r in sorted(mine, key=lambda r: r.get("taken_at") or "~")
                                 if r.get("taken")), None) \
        or next((BET_SIDE.get(r["tag"]) for r in mine if BET_SIDE.get(r["tag"])), None)
    seen = {}
    parts = []
    for full, short in BOOK_SHORT.items():
        ln = rec.get("lines", {}).get(full, {}).get(goalie)
        if ln and ln.get("point") is not None:
            seen[short] = {"point": ln["point"], "over": ln.get("over"), "under": ln.get("under")}
            price = ln.get(side.lower()) if side else None
            parts.append(f"{short} {(side[0].lower() if side else '')}{ln['point']}"
                         + (f" ({fmt_odds(price)})" if price is not None else ""))
        else:
            parts.append(f"{short} not yet")
    w[key] = {"side": side, "start": rec["commence_time"], "seen": seen, "last": None, "set": iso(now)}
    tg_reply(msg, f"👀 Watching {last_name(goalie)} until {fmt_time(rec['commence_time'], now)}: "
                  + " · ".join(parts) + f". I'll text you if the line or the price on your side moves "
                  f"(checks every {WATCH_MINUTES} min).")


def watch_check_due(state, event_id, event, now):
    w = state.get("watch") or {}
    keys = [k for k in w if k.startswith(f"{event_id}|")]
    if not keys or parse_iso(event["commence_time"]) <= now:
        return False
    return any(w[k]["last"] is None or now - parse_iso(w[k]["last"]) >= timedelta(minutes=WATCH_MINUTES)
               for k in keys)


def watch_compare(state, event, rec, current, abbrevs, now):
    """Compare a fresh odds pull with what each watched goalie showed last time; text the moves:
    '📈 DeSmith (DAL) line moved · 8:10PM / DK u25.5 → u26.5 ✅ better for your under'."""
    w = state.get("watch") or {}
    for key in [k for k in w if k.startswith(f"{event['id']}|")]:
        entry = w[key]
        goalie, side = key.split("|", 1)[1], entry.get("side")
        entry["last"] = iso(now)
        notes, up = [], None
        for full, short in BOOK_SHORT.items():
            ln = current.get(full, {}).get(goalie)
            if not ln or ln.get("point") is None:
                continue
            old = entry["seen"].get(short)
            entry["seen"][short] = {"point": ln["point"], "over": ln.get("over"), "under": ln.get("under")}
            if not old:
                continue  # newly posted book: the regular "(FD added)" alert covers it
            s = side[0].lower() if side else ""
            url = ln.get(side.lower() + "_link") if side else None
            if float(ln["point"]) != float(old["point"]):
                up = float(ln["point"]) > float(old["point"])
                good = None if not side else (up == (side == "UNDER"))
                notes.append(f"{short} {s}{old['point']} → {link(s + str(ln['point']), url)}"
                             + ("" if good is None else (" ✅ better for your " + side.lower() if good
                                                         else " ❌ worse for your " + side.lower())))
            elif side:
                a, b = implied(old.get(side.lower())), implied(ln.get(side.lower()))
                if a is not None and b is not None and abs(b - a) >= WATCH_PRICE_MOVE:
                    notes.append(f"{short} {link(s + str(ln['point']), url)} price {fmt_odds(old.get(side.lower()))}"
                                 f" → {fmt_odds(ln.get(side.lower()))}"
                                 + (" (line may move soon)" if b > a else " (moving away from your side)"))
        if notes:
            team = next((r.get("team") for r in load_picks() if r["event_id"] == event["id"]
                         and r["goalie"] == goalie and r.get("team")), "")
            name = f"{last_name(goalie)} ({team})" if team else last_name(goalie)
            icon = "📈" if up else "📉" if up is False else "💲"
            head = "line moved" if up is not None else "price moving"
            send_push("", f"{icon} {name} {head} · {fmt_time(event['commence_time'], now)}\n" + "\n".join(notes))
            print(f"WATCH {name}: {' | '.join(notes)}")
    state["watch"] = {k: v for k, v in w.items() if parse_iso(v["start"]) > now - timedelta(hours=6)}


def handle_manual_lines(requests, events, state, stats, abbrevs, injuries, now):
    """'line Talbot 24.5 DK': a line you can see at the book but the odds feed hasn't sent.
    The bot treats it like a posted line: full alert, tag, pick log, grading, `in` replies."""
    nicks = load_nicknames()
    upcoming = sorted((e for e in events if parse_iso(e["commence_time"]) > now),
                      key=lambda e: e["commence_time"])
    for msg, words in requests:
        book, point, name, typed = "draftkings", None, None, None
        for raw in words:
            w = raw.strip(",.:").lower()
            m_ = BET_TOKEN.match(w)
            if w in ("dk", "draftkings"):
                book = "draftkings"
            elif w in ("fd", "fanduel"):
                book = "fanduel"
            elif m_ and not (m_.group(1) or m_.group(4)):  # a plain number
                point = float(m_.group(3))
                point = point + 0.5 if point == int(point) else point
            elif w and w not in ("for", "at", "on", "the", "is", "o", "u", "over", "under"):
                if not name:
                    name, typed = w, raw.strip(",.:")
        if not name or point is None:
            tg_reply(msg, "Send it like: line Talbot 24.5 DK")
            continue
        keys = {team_key(name)} | nicks.get(team_key(name), set())
        found = None
        # A goalie the feed already has lines for: use that game.
        for event in upcoming:
            for p_ in {p for b in state["events"].get(event["id"], {}).get("lines", {}).values() for p in b}:
                if any(team_key(last_name(p_)).startswith(k) for k in keys):
                    found = (event, p_)
                    break
            if found:
                break
        for event in ([] if found else upcoming):
            for side in ("away", "home"):
                ab = abbrevs.get(team_key(event[f"{side}_team"]))
                if not ab:
                    continue
                roster = cached(state, f"roster_{ab}", now, ROSTER_REFRESH, lambda ab=ab: load_goalies(ab)) or []
                hit = next((g for g in roster if any(team_key(g.split()[-1]).startswith(k) for k in keys)), None)
                if hit:
                    found = (event, ascii_name(hit))
                    break
            if found:
                break
        if not found:
            tg_reply(msg, f"Couldn't find {typed} in today's upcoming games.")
            continue
        event, player = found
        rec = state["events"].setdefault(event["id"], {
            "matchup": f"{event['away_team']} @ {event['home_team']}",
            "commence_time": event["commence_time"], "lines": {}, "last_paid_check": None})
        if player in rec["lines"].get(book, {}):
            tg_reply(msg, f"{last_name(player)} is already posted at {BOOK_SHORT[book]} "
                          f"({rec['lines'][book][player].get('point')}). Text resend {last_name(player)} to see it.")
            continue
        known_before = {p for players in rec["lines"].values() for p in players}
        rec["lines"].setdefault(book, {})[player] = {"point": point, "over": None, "under": None, "manual": True}
        alert_new_lines(event, rec, {(book, player)}, known_before, matchup(event, stats), stats,
                        state, injuries, now)


def handle_resends(resends, state, stats, abbrevs, injuries, now):
    """'resend Wallstedt' (or swipe-reply 'resend' on any alert): send that goalie's full alert
    again with the latest lines, tags, H2H, last-5 and injuries. Free (no odds call)."""
    if not resends:
        return
    rows = load_picks()
    for msg, names in resends:
        target = state["sent"].get(str((msg.get("reply_to_message") or {}).get("message_id")))
        wanted = [(target["event_id"], target["goalie"])] if target else []
        for name in names:
            found = find_by_name(rows, name.strip(",."), now)
            if found:
                wanted.append(found)
            else:
                tg_reply(msg, f"Couldn't find {name} in the last two days of alerts.")
        if not wanted and not names:
            tg_reply(msg, "Type a goalie's last name, like: resend Wallstedt")
        for event_id, goalie in wanted:
            rec = state["events"].get(event_id)
            if not rec or " @ " not in rec.get("matchup", ""):
                tg_reply(msg, f"{last_name(goalie)}'s game is too old to resend.")
                continue
            away, home = rec["matchup"].split(" @ ", 1)
            event = {"id": event_id, "away_team": away, "home_team": home,
                     "commence_time": rec["commence_time"]}
            m = matchup(event, stats)
            sides = goalie_sides(event, {goalie}, state, now) if m else {}
            h2h = get_h2h(state, abbrevs.get(team_key(away)), abbrevs.get(team_key(home)), now)
            pairs = {(b, goalie) for b, players in rec.get("lines", {}).items() if goalie in players}
            for text, player, book in build_messages(
                    event, pairs, rec["lines"], m, sides, abbrevs, h2h, set(), True,
                    (stats or {}).get("raw"), (state.get("game_log") or {}).get("games"),
                    injuries, state, now):
                mid = send_push("", text)
                if mid:  # so you can swipe-reply "in" on the resent alert too
                    state["sent"][str(mid)] = {"event_id": event_id, "goalie": player,
                                               "book": None, "at": iso(now)}


# ---------- main ----------

def run_test():
    events, remaining = api_get(f"/sports/{SPORT}/events", {})
    n = len(events or [])
    msg = (f"Test alert works. The Odds API key is valid; {n} upcoming NHL games listed."
           + (f" Credits left: {remaining}." if remaining is not None else ""))
    print(msg)
    send_push("Saves alerts: test", msg, silent=False)


def main():
    if not ODDS_API_KEY:
        sys.exit("Missing ODDS_API_KEY.")
    if TEST_PUSH:
        run_test()
        return

    state = load_state()
    now = datetime.now(timezone.utc)

    resends, manual_lines = process_replies(state, now)  # your "in" replies and "resend" requests (free)

    # Grade yesterday's picks against box scores (free; once each morning).
    try:
        recheck_corrections(state, now)  # stat corrections on the last two nights (free, once a morning)
    except Exception as e:
        print(f"Correction check skipped ({e}).")
    graded = grade_picks(state, now)
    # Bets already texted the night they ended: list them for the model, not under "Your bets".
    night = state.setdefault("night_graded", {})
    today = now.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")
    due = [d for d in night if d < today] if now.astimezone(LOCAL_TZ).hour >= GRADE_AFTER_HOUR else []
    skip = {k for d in due for k in night[d]}
    if due:
        have = {(r["event_id"], r["goalie"], r["book"]) for r in graded}
        graded += [r for r in load_picks() if r["date"] in due and r.get("result")
                   and f"{r['event_id']}|{r['goalie']}" in skip
                   and (r["event_id"], r["goalie"], r["book"]) not in have]
        for d in due:
            night.pop(d, None)
    if graded:
        dates = sorted({r["date"] for r in graded})
        title = "Saves results: " + ", ".join(
            datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d") for d in dates)
        abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
        send_push(title, results_message(graded, abbrevs, skip))
        print(f"Graded {len(graded)} pick(s) from {', '.join(dates)}")
    try:
        live_results(state, now)  # your bets, texted as each game ends (free)
    except Exception as e:
        print(f"Live results skipped ({e}).")
    try:
        channel_catchup(state)  # results to the picks channel
    except Exception as e:
        print(f"Picks channel results skipped ({e}).")

    events, remaining = api_get(f"/sports/{SPORT}/events", {
        "commenceTimeFrom": iso(now),
        "commenceTimeTo": iso(now + timedelta(hours=LOOKAHEAD_HOURS)),
    })
    events = [e for e in (events or []) if wanted(e)]
    print(f"{len(events)} upcoming game(s) in the next {LOOKAHEAD_HOURS}h"
          + (f" (filter: {', '.join(TEAMS)})" if TEAMS else ""))

    stats = get_shot_stats(state, now) if SHOT_THRESHOLD > 0 else None
    if SHOT_THRESHOLD > 0:
        print(f"Matchup filter: ±{SHOT_THRESHOLD:g} shots"
              + (f" (league avg {stats['avg_shots']:.1f} shots, save% {stats['save_pct']:.3f}, "
                 f"{'opponent-adjusted' if stats.get('adjusted') else 'raw'})"
                 if stats else " — stats unavailable, watching every game"))

    credits = remaining
    alerts = checks = skipped_rechecks = skipped_games = skipped_nolean = 0

    # Key-player injuries (free). Change alerts go out when a key player is ruled OUT for a
    # game you've already been alerted on.
    abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
    injuries, newly_out, newly_back = injury_report(state, events, abbrevs, now) if abbrevs else ({}, [], [])
    for team, k in newly_out:
        send_injury_change(state, events, stats, abbrevs, team, k, now)
    for team, k in newly_back:
        send_injury_change(state, events, stats, abbrevs, team, k, now, back=True)
    handle_resends(resends, state, stats, abbrevs, injuries, now)
    handle_manual_lines(manual_lines, events, state, stats, abbrevs, injuries, now)

    for event in events:
        eid = event["id"]
        m = matchup(event, stats)
        if not watch_game(m):
            skipped_games += 1
            print(f"Middling matchup (no lean either side): {event['away_team']} @ "
                  f"{event['home_team']} | " + fmt_matchup(m))
            if SKIP_MIDDLING_GAMES:
                continue
        rec = state["events"].setdefault(eid, {
            "matchup": f"{event['away_team']} @ {event['home_team']}",
            "commence_time": event["commence_time"],
            "lines": {},
            "last_paid_check": None,
        })
        rec["commence_time"] = event["commence_time"]

        watch_due = watch_check_due(state, eid, event, now)
        if is_complete(rec) and not watch_due:
            continue

        if credits is not None and credits < MIN_CREDITS:
            if not state["low_credit_warned"]:
                send_push("Saves alerts paused",
                          f"Only {credits} Odds API credits left this month, so checks are "
                          f"paused until the quota resets.", silent=False)
                state["low_credit_warned"] = True
            print(f"Credits low ({credits}); skipping remaining checks.")
            break

        has_lines = any(rec["lines"].values())
        if has_lines and not watch_due:
            # Rechecking a partly-posted game costs a credit, so pace it.
            starts_in = parse_iso(event["commence_time"]) - now
            last = rec.get("last_paid_check")
            due = last is None or now - parse_iso(last) >= timedelta(minutes=RECHECK_MINUTES)
            in_window = starts_in <= timedelta(hours=RECHECK_WINDOW_HOURS)
            budget_ok = credits is None or credits > RECHECK_RESERVE
            # Final checks: late starter confirmations land in the last hour, so every incomplete
            # game (lean or not) gets a check at each FINAL_CHECKS mark, e.g. 45 and 20 min before
            # puck drop. A check that already happened after a mark counts for it.
            start = parse_iso(event["commence_time"])
            last_call = budget_ok and any(
                starts_in <= timedelta(minutes=mark) and
                (last is None or parse_iso(last) < start - timedelta(minutes=mark))
                for mark in FINAL_CHECKS)
            last_call = last_call or (budget_ok and timedelta(0) < starts_in <= timedelta(minutes=PRIORITY_WINDOW)
                                      and priority_game(event, stats))
            if not last_call and not (due and in_window and budget_ok):
                skipped_rechecks += 1
                continue
            if not last_call and not lean_goalie_missing(event, rec, m, state, now):
                # Only no-lean goalies left to post: recheck far less often (or never).
                nolean_due = NOLEAN_RECHECK_MINUTES > 0 and (
                    last is None or now - parse_iso(last) >= timedelta(minutes=NOLEAN_RECHECK_MINUTES))
                if not nolean_due:
                    skipped_nolean += 1
                    continue

        data, rem = api_get(f"/sports/{SPORT}/events/{eid}/odds", {
            "bookmakers": ",".join(BOOKS),
            "markets": MARKET,
            "oddsFormat": "american",
            "includeLinks": "true",  # tap-to-bet links (free with the same call)
        })
        checks += 1
        if rem is not None:
            credits = rem
        current = extract_lines(data)
        if not current:
            continue  # nothing posted (free)

        rec["last_paid_check"] = iso(now)
        if watch_due:
            watch_compare(state, event, rec, current, abbrevs, now)  # before rec lines are updated
        known_before = {p for players in rec["lines"].values() for p in players}
        new_pairs = {(book, player)
                     for book, players in current.items()
                     for player in players
                     if player not in rec["lines"].get(book, {})}
        # Keep every goalie we've ever seen, updated with the latest numbers.
        for book, players in current.items():
            rec["lines"].setdefault(book, {}).update(players)

        if new_pairs:
            alert_new_lines(event, rec, new_pairs, known_before, m, stats, state, injuries, now)
            alerts += 1

    # Reset the low-credit warning once credits recover (new month).
    if credits is not None and credits >= MIN_CREDITS:
        state["low_credit_warned"] = False

    # Forget games that started more than two days ago.
    cutoff = now - timedelta(days=2)
    state["events"] = {k: v for k, v in state["events"].items()
                       if parse_iso(v["commence_time"]) > cutoff}
    old = iso(now - timedelta(days=3))
    state["sent"] = {k: v for k, v in state["sent"].items() if v.get("at", "") > old}
    state["credits_remaining"] = credits
    save_state(state)
    print(f"Done: {checks} odds check(s), {alerts} alert(s), "
          f"{skipped_rechecks} recheck(s) not due yet, {skipped_nolean} recheck(s) held back (only no-lean "
          f"goalies missing), {skipped_games} middling game(s), "
          f"credits remaining: {credits}")


if __name__ == "__main__":
    main()
