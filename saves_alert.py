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
  TEST_PUSH             "true" = send a test notification and exit
"""

import json
import os
import sys
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
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
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
MIN_CREDITS = env_int("MIN_CREDITS", 20)
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


def fmt_time(commence):
    local = parse_iso(commence).astimezone(LOCAL_TZ)
    return local.strftime("%a %-I:%M %p").replace(":00 ", " ")


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
        "text": f"{title}\n{message}"[:4096],
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


def wanted(event):
    if not TEAMS:
        return True
    teams = f"{event.get('home_team', '')} {event.get('away_team', '')}".lower()
    return any(t in teams for t in TEAMS)


def is_complete(rec):
    return all(len(rec["lines"].get(b, {})) >= GOALIES_PER_GAME for b in BOOKS)


def build_message(event, new_pairs, current):
    """new_pairs: set of (book, player) just posted. current: all lines now."""
    header = f"{event['away_team']} @ {event['home_team']} · {fmt_time(event['commence_time'])}"
    rows = []
    for player in sorted({p for _, p in new_pairs}):
        parts = []
        for book in BOOKS:
            ln = current.get(book, {}).get(player)
            short = BOOK_SHORT.get(book, book)
            if ln:
                tag = " (new)" if (book, player) in new_pairs else ""
                parts.append(f"{short} {ln.get('point')} ({fmt_odds(ln.get('over'))}/"
                             f"{fmt_odds(ln.get('under'))}){tag}")
            else:
                parts.append(f"{short} not yet")
        rows.append(f"{player}\n  " + " · ".join(parts))
    return header + "\n" + "\n".join(rows)


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

    events, remaining = api_get(f"/sports/{SPORT}/events", {
        "commenceTimeFrom": iso(now),
        "commenceTimeTo": iso(now + timedelta(hours=LOOKAHEAD_HOURS)),
    })
    events = [e for e in (events or []) if wanted(e)]
    print(f"{len(events)} upcoming game(s) in the next {LOOKAHEAD_HOURS}h"
          + (f" (filter: {', '.join(TEAMS)})" if TEAMS else ""))

    credits = remaining
    alerts = checks = skipped_rechecks = 0

    for event in events:
        eid = event["id"]
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
            if not (due and in_window and budget_ok):
                skipped_rechecks += 1
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
        new_pairs = {(book, player)
                     for book, players in current.items()
                     for player in players
                     if player not in rec["lines"].get(book, {})}
        # Keep every goalie we've ever seen, updated with the latest numbers.
        for book, players in current.items():
            rec["lines"].setdefault(book, {}).update(players)

        if new_pairs:
            send_push("Goalie saves posted", build_message(event, new_pairs, rec["lines"]))
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
          f"{skipped_rechecks} recheck(s) not due yet, credits remaining: {credits}")


if __name__ == "__main__":
    main()
