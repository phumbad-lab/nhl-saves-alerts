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
PICK_FIELDS = ["date", "game", "goalie", "team", "book", "line", "over_odds", "under_odds",
               "expected_saves", "tag", "actual_saves", "outcome", "result",
               "event_id", "commence_time", "away_team", "home_team", "logged_at", "fire"]
GRADE_AFTER_HOUR = 7  # grade yesterday's games once it's past 7 AM Eastern
GOALIES_PER_GAME = 2


def env_int(name, default):
    return int(os.getenv(name, "") or default)


ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SILENT = (os.getenv("TELEGRAM_SILENT", "") or "true").strip().lower() in ("1", "true", "yes")
TEAMS = [t.strip().lower() for t in os.getenv("TEAMS", "").split(",") if t.strip()]
BOOKS = [b.strip().lower() for b in (os.getenv("BOOKS", "") or "draftkings,fanduel").split(",") if b.strip()]
LOOKAHEAD_HOURS = env_int("LOOKAHEAD_HOURS", 30)
RECHECK_MINUTES = env_int("RECHECK_MINUTES", 60)
RECHECK_WINDOW_HOURS = env_int("RECHECK_WINDOW_HOURS", 10)
RECHECK_RESERVE = env_int("RECHECK_RESERVE", 150)
# Goalies with no lean (always "no edge") are rechecked this often while missing; 0 = never.
NOLEAN_RECHECK_MINUTES = 180
FINAL_CHECK_MINUTES = 75  # one last recheck of any game still missing a goalie, this long before puck drop
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
STATS_VERSION = 4  # bump when the saved stats format changes
OPPONENT_ADJUST = True  # rate shots for/against vs. the strength of opponents faced
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


def send_push(title, message, silent=None):
    """Send a Telegram message from your bot to your chat."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print(f"[dry run, no Telegram keys] {title}\n{message}\n")
        return
    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": (f"{title}\n{message}" if title else message)[:4096],
        "disable_notification": "true" if (SILENT if silent is None else silent) else "false",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(url, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if not result.get("ok"):
                print(f"Telegram error: {result}")
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


def adjusted_team_stats(games, abbrev_to_key):
    """Opponent-adjusted shots for/against per team, overall and home/road, from the game log."""
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
        return sum(vals) / len(vals) if vals else lg

    teams = {}
    for team, glist in by_team.items():
        rows = []
        for g in glist:
            sf_adj = g["sf"] - (opp_avg(g["opp"], "sa", team) - lg)  # vs. how much opp usually allows
            sa_adj = g["sa"] - (opp_avg(g["opp"], "sf", team) - lg)  # vs. how much opp usually shoots
            rows.append((sf_adj, sa_adj, g["home"]))

        def summary(sub):
            return ({"sf": sum(r[0] for r in sub) / len(sub), "sa": sum(r[1] for r in sub) / len(sub),
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


def fmt_h2h(h2h, ab):
    """Two lines: shots faced by each team's goalie in recent meetings, newest first."""
    if not h2h:
        return []
    lines = []
    for i, team in enumerate((ab["away"], ab["home"])):
        faced = [(g[4] if g[1] == team else g[3]) for g in h2h]  # opponent's shots = shots on this goalie
        nums = ", ".join(str(x) for x in faced)
        lines.append(f"H2H L{len(h2h)}: on {team} {nums} (avg {sum(faced) / len(faced):.1f})")
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
            teams, lg = adjusted_team_stats(update_game_log(state, now),
                                            {ab: key for key, ab in abbrevs.items()})
            if teams and len(teams) >= 20:
                fresh.update(teams=teams, avg_shots=round(lg, 2), adjusted=True)
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
        out[side] = {"team": nickname(name), "shots": shots, "saves": shots * sv,
                     "delta": shots - avg}
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


def tag_code(expected, point, delta):
    """The matchup picks the direction; the line picks the strength.
    delta = goalie's expected shots minus league average.
      delta >= +SHOT_THRESHOLD (overs only):  line <= expected -> OVER,
          line within LEAN_SAVES above expected -> LEAN_OVER, else FADE (never an under)
      delta <= -SHOT_THRESHOLD (unders only): mirror image -> UNDER / LEAN_UNDER / FADE
      otherwise (middling): FADE"""
    if expected is None or point is None or delta is None:
        return ""
    edge = max(SHOT_THRESHOLD, 0.01)
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


def target_tag(expected, point, delta, side=None, ctx=None):
    code = tag_code(expected, point, delta)
    if not code:
        return ""
    fire = " 🔥" if is_fire(code, expected, point, side, ctx) else ""
    return f" {TAG_LABELS[code]}{fire}"


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


def log_picks(event, new_pairs, lines, m, sides, abbrevs, now, h2h=None, raw=None):
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
            if r["date"] not in schedules:
                schedules[r["date"]] = nhl_get(f"{NHL_WEB}/score/{r['date']}").get("games", [])
            away = abbrevs.get(team_key(r["away_team"]))
            home = abbrevs.get(team_key(r["home_team"]))
            game = next((g for g in schedules[r["date"]]
                         if g["awayTeam"]["abbrev"] == away and g["homeTeam"]["abbrev"] == home), None)
            if not game:
                continue
            if game.get("gameScheduleState", "OK") != "OK":
                r.update(outcome="VOID", result="VOID")  # postponed / cancelled
                graded.append(r)
                continue
            if game.get("gameState") not in ("OFF", "FINAL"):
                continue
            if game["id"] not in boxes:
                boxes[game["id"]] = boxscore_goalies(game["id"])
        except Exception as e:
            print(f"Couldn't grade {r['goalie']} ({e}); will retry next run.")
            continue
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
        graded.append(r)
    if graded:
        save_picks(rows)
    return graded


def record_line(rows, tag):
    """W-L-P for a tag, counting each goalie/line once even if both books posted it."""
    seen, w, l, p = set(), 0, 0, 0
    for r in rows:
        if r.get("tag") != tag or r.get("result") not in ("W", "L", "P"):
            continue
        key = (r["event_id"], r["goalie"], r["line"])
        if key in seen:
            continue
        seen.add(key)
        w += r["result"] == "W"; l += r["result"] == "L"; p += r["result"] == "P"
    return w, l, p


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


def results_message(graded, abbrevs=None):
    abbrevs = abbrevs or {}
    lines, seen = [], set()
    for r in sorted(graded, key=lambda r: (r["date"], r["game"], r["goalie"], r["book"])):
        if r["outcome"] == "VOID":
            key = (r["event_id"], r["goalie"], "void")
            if key not in seen:
                seen.add(key)
                lines.append(f"{who(r, abbrevs)}: didn't play (void)")
            continue
        key = (r["event_id"], r["goalie"], r["line"])
        books = [x["book"] for x in graded if (x["event_id"], x["goalie"], x["line"]) == key]
        if key in seen:
            continue
        seen.add(key)
        label = {"OVER": f"o{r['line']} OVER", "LEAN_OVER": f"o{r['line']} LEAN OVER",
                 "UNDER": f"u{r['line']} UNDER", "LEAN_UNDER": f"u{r['line']} LEAN UNDER"}.get(
                     r["tag"], f"{r['line']} NO EDGE")
        if r.get("fire") == "1":
            label += " 🔥"
        mark = {"W": " ✅", "L": " ❌", "P": " push"}.get(r["result"], f" → went {r['outcome'].lower()}")
        lines.append(f"{who(r, abbrevs)} {label} ({'/'.join(books)}): {r['actual_saves']} saves{mark}")
    all_rows = load_picks()
    season = " · ".join(f"{TAG_LABELS[t]} {fmt_record(*record_line(all_rows, t))}"
                        for t in ("OVER", "LEAN_OVER", "UNDER", "LEAN_UNDER"))
    fire_rows = [r for r in all_rows if r.get("fire") == "1"]
    season += " · 🔥 " + fmt_record(*[a + b for a, b in zip(record_line(fire_rows, "OVER"),
                                                          record_line(fire_rows, "UNDER"))])
    return "\n".join(lines) + "\n\nSeason: " + season


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


RECENT_GAMES = 4  # games listed on the "L4 For / L4 Against" lines


def recent_games(games, team, stat, n=RECENT_GAMES):
    """Last n games for a team, newest first, as '43-TOR 28-SEA ...'.
    stat 'sf' = shots the team took, 'sa' = shots it allowed. Raw numbers."""
    out = []
    for d, a, h, asog, hsog in sorted(games or [], key=lambda g: g[0], reverse=True):
        if team not in (a, h):
            continue
        away = team == a
        shots = (asog if away else hsog) if stat == "sf" else (hsog if away else asog)
        out.append(f"{shots}-{h if away else a}")
        if len(out) == n:
            break
    return out


def rank_line(event, side, ab, raw, games=None):
    """Two lines, e.g.
        VGK L4 For: 43-TOR 28-SEA 28-VAN 30-ANA (3rd most 33.2)
        LAK L4 Against: 30-FLA 25-SJS 29-COL (15th most 28.0)
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
        label = f"L{len(recent)} {word}: " + " ".join(recent) + " " if recent else f"{word}: "
        return f"{team} {label}({place(key, stat)} {raw[key][stat]:.1f})"
    return [line(ab[other], opp, "sf", "For"), line(ab[side], own, "sa", "Against")]


def book_parts(player, current, expected, delta, side=None, ctx=None):
    parts = []
    for book in BOOKS:
        ln = current.get(book, {}).get(player)
        short = BOOK_SHORT.get(book, book)
        if ln:
            parts.append(f"{short} {ln.get('point')}{target_tag(expected, ln.get('point'), delta, side, ctx)}")
        else:
            parts.append(f"{short} not yet")
    return parts


def build_message(event, new_pairs, current, m=None, sides=None, abbrevs=None, h2h=None,
                  known_before=(), show_h2h=True, raw=None, games=None):
    """One message per game per run.
    Goalies seen for the first time get a full block:
        Kuemper (LAK) - LAK@VGK 10:10PM
        DK 26.5 OVER · FD not yet
        30.9 shots, 27.3 saves expected
        H2H L4: on LAK 25, 22, 27, 35 (avg 27.2)            <- once per game
        H2H L4: on VGK 19, 33, 24, 26 (avg 25.5)
        VGK L4 For: 43-TOR 28-SEA 28-VAN 30-ANA (3rd most 33.2)
        LAK L4 Against: 30-FLA 25-SJS 29-COL 22-BOS (15th most 28.0)
    A goalie already alerted who shows up at the other book gets one line:
        Kuemper (LAK) 26.5 OVER · 10:10PM (FD added)"""
    sides, abbrevs = sides or {}, abbrevs or {}
    ab = {s: abbrevs.get(team_key(event[f"{s}_team"])) or nickname(event[f"{s}_team"])
          for s in ("away", "home")}
    ctx = fire_context(event, ab, h2h, raw, m)
    new_goalies = sorted({p for _, p in new_pairs if p not in known_before})
    added = sorted((b, p) for b, p in new_pairs if p in known_before)
    out = []
    when = fmt_time(event['commence_time'])
    game = f"{ab['away']}@{ab['home']} {when}"
    for i, player in enumerate(new_goalies):
        if out:
            out.append("")  # blank line between goalies
        side = sides.get(player)
        g = m[side] if (m and side) else None
        expected, delta = (g["saves"], g["delta"]) if g else (None, None)
        label = f"{last_name(player)} ({ab[side]})" if side else last_name(player)
        out.append(f"{label} - {game}")
        out.append(" · ".join(book_parts(player, current, expected, delta, side, ctx)))
        if g:
            out.append(f"{g['shots']:.1f} shots, {g['saves']:.1f} saves expected")
        elif m:
            out.append(f"Expected saves: {ab['away']} goalie {m['away']['saves']:.1f} / "
                       f"{ab['home']} goalie {m['home']['saves']:.1f} (team unknown)")
        if i == 0 and show_h2h:
            out.extend(fmt_h2h(h2h, ab))
        if side:
            out.extend(rank_line(event, side, ab, raw, games))
    for book, player in added:
        side = sides.get(player)
        g = m[side] if (m and side) else None
        ln = current.get(book, {}).get(player, {})
        tag = target_tag(g["saves"] if g else None, ln.get("point"), g["delta"] if g else None, side, ctx)
        who_ = (f"{last_name(player)} ({ab[side]})" if side
                else f"{last_name(player)} ({ab['away']}@{ab['home']})")
        out.append(f"{who_} {ln.get('point')}{tag} · {when} ({BOOK_SHORT.get(book, book)} added)")
    return "\n".join(out)


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

    # Grade yesterday's picks against box scores (free; once each morning).
    graded = grade_picks(state, now)
    if graded:
        dates = sorted({r["date"] for r in graded})
        title = "Saves results: " + ", ".join(
            datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d") for d in dates)
        abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
        send_push(title, results_message(graded, abbrevs))
        print(f"Graded {len(graded)} pick(s) from {', '.join(dates)}")

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

        if is_complete(rec):
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
        if has_lines:
            # Rechecking a partly-posted game costs a credit, so pace it.
            starts_in = parse_iso(event["commence_time"]) - now
            last = rec.get("last_paid_check")
            due = last is None or now - parse_iso(last) >= timedelta(minutes=RECHECK_MINUTES)
            in_window = starts_in <= timedelta(hours=RECHECK_WINDOW_HOURS)
            budget_ok = credits is None or credits > RECHECK_RESERVE
            # Last call: once inside the final window before puck drop, every incomplete game
            # gets one more check (lean or not, hourly timer or not), since late confirmations land then.
            final_window = timedelta(minutes=FINAL_CHECK_MINUTES)
            last_call = (FINAL_CHECK_MINUTES > 0 and starts_in <= final_window and budget_ok and
                         (last is None or parse_iso(last) < parse_iso(event["commence_time"]) - final_window))
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
        })
        checks += 1
        if rem is not None:
            credits = rem
        current = extract_lines(data)
        if not current:
            continue  # nothing posted (free)

        rec["last_paid_check"] = iso(now)
        known_before = {p for players in rec["lines"].values() for p in players}
        new_pairs = {(book, player)
                     for book, players in current.items()
                     for player in players
                     if player not in rec["lines"].get(book, {})}
        # Keep every goalie we've ever seen, updated with the latest numbers.
        for book, players in current.items():
            rec["lines"].setdefault(book, {}).update(players)

        if new_pairs:
            sides = goalie_sides(event, {p for _, p in new_pairs}, state, now) if m else {}
            abbrevs = cached(state, "team_abbrevs", now, timedelta(days=1), load_abbrevs) or {}
            h2h = get_h2h(state, abbrevs.get(team_key(event["away_team"])),
                          abbrevs.get(team_key(event["home_team"])), now)
            show_h2h = not rec.get("h2h_sent")
            send_push("", build_message(event, new_pairs, rec["lines"], m, sides, abbrevs, h2h,
                                        known_before, show_h2h, (stats or {}).get("raw"),
                                        (state.get("game_log") or {}).get("games")))
            if show_h2h and h2h and any(p not in known_before for _, p in new_pairs):
                rec["h2h_sent"] = True
            log_picks(event, new_pairs, rec["lines"], m, sides, abbrevs, now, h2h, (stats or {}).get("raw"))
            alerts += 1
            names = ", ".join(f"{p} ({BOOK_SHORT.get(b, b)})" for b, p in sorted(new_pairs))
            print(f"ALERT {rec['matchup']}: {names}")

    # Reset the low-credit warning once credits recover (new month).
    if credits is not None and credits >= MIN_CREDITS:
        state["low_credit_warned"] = False

    # Forget games that started more than two days ago.
    cutoff = now - timedelta(days=2)
    state["events"] = {k: v for k, v in state["events"].items()
                       if parse_iso(v["commence_time"]) > cutoff}
    state["credits_remaining"] = credits
    save_state(state)
    print(f"Done: {checks} odds check(s), {alerts} alert(s), "
          f"{skipped_rechecks} recheck(s) not due yet, {skipped_nolean} recheck(s) held back (only no-lean "
          f"goalies missing), {skipped_games} middling game(s), "
          f"credits remaining: {credits}")


if __name__ == "__main__":
    main()
