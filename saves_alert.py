"""
NHL goalie saves prop alerts for DraftKings and FanDuel.

Checks The Odds API for the `player_total_saves` market on upcoming NHL games and
sends a Telegram message the first time each sportsbook posts saves lines
for a game.

Credit-saving design (The Odds API free plan = 500 credits/month):
  * Listing games (/events) is free.
  * Asking for a market that isn't posted yet returns empty data, which is free.
  * Each book is checked separately and dropped once it has posted, so each
    game costs about 1 credit per book (~2 credits per game total).

Environment variables:
  ODDS_API_KEY        The Odds API key (required)
  TELEGRAM_BOT_TOKEN  Token from @BotFather (required to send alerts)
  TELEGRAM_CHAT_ID    Your chat ID with the bot (required to send alerts)
  TELEGRAM_SILENT     "true" (default) = alerts arrive without sound; "false" = normal
  TEAMS               Optional comma-separated filter, e.g. "Red Wings,Rangers".
                      Empty = all games.
  BOOKS               Optional, default "draftkings,fanduel"
  LOOKAHEAD_HOURS     How far ahead to look for games (default 30)
  MIN_CREDITS         Stop spending credits below this many remaining (default 20)
  TEST_PUSH           "true" = send a test notification and exit
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

API = "https://api.the-odds-api.com/v4"
SPORT = "icehockey_nhl"
MARKET = "player_total_saves"
BOOK_NAMES = {"draftkings": "DraftKings", "fanduel": "FanDuel"}
BOOK_SHORT = {"draftkings": "DK", "fanduel": "FD"}
LOCAL_TZ = ZoneInfo("America/New_York")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SILENT = (os.getenv("TELEGRAM_SILENT", "") or "true").strip().lower() in ("1", "true", "yes")
TEAMS = [t.strip().lower() for t in os.getenv("TEAMS", "").split(",") if t.strip()]
BOOKS = [b.strip().lower() for b in (os.getenv("BOOKS", "") or "draftkings,fanduel").split(",") if b.strip()]
LOOKAHEAD_HOURS = int(os.getenv("LOOKAHEAD_HOURS", "") or "30")
MIN_CREDITS = int(os.getenv("MIN_CREDITS", "") or "20")
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
    req = urllib.request.Request(url, headers={"User-Agent": "nhl-saves-alerts/1.0"})
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


def load_state():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    state.setdefault("events", {})
    state.setdefault("low_credit_warned", False)
    return state


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def extract_lines(event_odds, book):
    """Return {player: {"point": x, "over": price, "under": price}} for one book."""
    lines = {}
    for bm in (event_odds or {}).get("bookmakers", []):
        if bm.get("key") != book:
            continue
        for market in bm.get("markets", []):
            if market.get("key") != MARKET:
                continue
            for o in market.get("outcomes", []):
                player = o.get("description") or "Unknown"
                entry = lines.setdefault(player, {"point": o.get("point")})
                side = (o.get("name") or "").lower()
                if side in ("over", "under"):
                    entry[side] = o.get("price")
                    if o.get("point") is not None:
                        entry["point"] = o.get("point")
    return lines


def wanted(event):
    if not TEAMS:
        return True
    teams = f"{event.get('home_team', '')} {event.get('away_team', '')}".lower()
    return any(t in teams for t in TEAMS)


def build_message(event, book, lines, other_lines):
    header = f"{event['away_team']} @ {event['home_team']} · {fmt_time(event['commence_time'])}"
    rows = []
    for player, ln in sorted(lines.items()):
        row = f"{player}: O/U {ln.get('point')} ({fmt_odds(ln.get('over'))}/{fmt_odds(ln.get('under'))})"
        for other_book, olines in other_lines.items():
            o = olines.get(player)
            if o:
                row += f" | {BOOK_SHORT.get(other_book, other_book)} {o.get('point')}"
        rows.append(row)
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
    alerts = 0
    calls = 0

    for event in events:
        eid = event["id"]
        rec = state["events"].setdefault(eid, {
            "matchup": f"{event['away_team']} @ {event['home_team']}",
            "commence_time": event["commence_time"],
            "posted": {},
        })
        rec["commence_time"] = event["commence_time"]

        for book in BOOKS:
            if book in rec["posted"]:
                continue
            if credits is not None and credits < MIN_CREDITS:
                if not state["low_credit_warned"]:
                    send_push("Saves alerts paused",
                              f"Only {credits} Odds API credits left this month, so checks are paused "
                              f"until the quota resets.", silent=False)
                    state["low_credit_warned"] = True
                print(f"Credits low ({credits}); skipping remaining checks.")
                break

            if calls:
                time.sleep(1)  # be gentle with the API
            data, rem = api_get(f"/sports/{SPORT}/events/{eid}/odds", {
                "bookmakers": book,
                "markets": MARKET,
                "oddsFormat": "american",
            })
            calls += 1
            if rem is not None:
                credits = rem
            lines = extract_lines(data, book)
            if not lines:
                continue  # not posted yet (empty response = no credit used)

            other = {b: v["lines"] for b, v in rec["posted"].items()}
            title = f"{BOOK_NAMES.get(book, book)}: goalie saves posted"
            send_push(title, build_message(event, book, lines, other))
            rec["posted"][book] = {"at": iso(now), "lines": lines}
            alerts += 1
            print(f"ALERT {title}: {rec['matchup']}")

    # Reset the low-credit warning once credits recover (new month).
    if credits is not None and credits >= MIN_CREDITS:
        state["low_credit_warned"] = False

    # Forget games that started more than two days ago.
    cutoff = now - timedelta(days=2)
    state["events"] = {k: v for k, v in state["events"].items()
                       if parse_iso(v["commence_time"]) > cutoff}
    state["credits_remaining"] = credits
    save_state(state)
    print(f"Done: {calls} odds check(s), {alerts} alert(s), credits remaining: {credits}")


if __name__ == "__main__":
    main()
