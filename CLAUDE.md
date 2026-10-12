# NHL goalie saves alerts — working notes

Read this before changing anything here. It records who this is for, how the model works,
what's been decided and why, and what's still pending. Keep it current when things change.

## The owner and how he works
- Bets NHL goalie **saves** props on DraftKings (DK) and FanDuel (FD) for fun. ~58% last year, likes 2-leg parlays. Tracks real bets in Pikkit.
- A separate "shots partner" project (shots on goal) lives in its own repo/thread. It **shares this Telegram bot and the Odds API key**. It only sends messages; only this repo reads replies (`getUpdates`). If the shots app ever starts reading replies, the two will steal each other's messages, so give it its own bot first.
- **Don't build rules on hunches.** "I don't want to build inaccurate rules." Model changes get tested against graded results first (shadow numbers, retro tests), then he approves. Never change model math without his OK.
- Cost: was strictly free; on **Oct 10 2026 he moved to the Odds API $30/month plan (20,000 credits)** for a month of tuning. See "If he goes back to free" below.
- Alert style he chose: last names, team abbreviations, ALL-CAPS tags, no odds in alerts (lines move too much; the 🔥 tells him when to act fast), short lines that are easy to search by last name.
- Explain things plainly, no jargon. He reads alerts on his iPhone (Telegram, badge-only).

## How it runs
- `saves_alert.py` runs on GitHub Actions (`.github/workflows/saves-alert.yml`), triggered **every minute** by cron-job.org (POST to the workflow_dispatch API); the built-in GitHub schedule (every 15 min, all day) is a backup. The owner pauses the cron-job.org saves job overnight (midnight–6 AM ET as of Oct 12; it was 9 AM once, which skipped the 7 AM results until a manual run). The backup was widened to all day so results go out at 7 AM regardless. If runs stop, check the cron-job.org job first. Repo is public, so Actions minutes are free.
- Secrets: `ODDS_API_KEY` (new key issued Oct 10 with the paid plan), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Variables currently set: `RECHECK_MINUTES=15`, `RECHECK_RESERVE=1000`.
- The bot commits `state.json` and `picks.csv` after runs ("Update alert state"). **Those two files are the bot's. Never edit or commit them by hand**, and never ask the owner to upload them.
- **Pushing changes (Claude):** edit only code/docs, `git pull --rebase origin main` right before committing and pushing (the bot pushes often), `git add` the specific files only, push to `main`. Test first with the scratch harnesses (copy the script + a copy of live `picks.csv`/`state.json` into a scratch dir; never run it inside the repo, and delete `__pycache__`).
- **Repo stays public** (owner's call, Oct 11): free unlimited Actions minutes make every-minute runs possible; private would cap at 2,000 min/month. Code, picks.csv and his logged bets are publicly visible; secrets are not. Revisit if he ever shares or sells picks (move the runner somewhere private).
- Odds API: market `player_total_saves`; one call covers both books; a response with lines costs 1 credit, an empty one is free, `/events` is free.

## The model (current)
- **Expected shots on a goalie** = (opponent shots-for per game + own team shots-against per game) / 2, using this season's NHL team stats only.
  - **Opponent-adjusted** (`OPPONENT_ADJUST = True`): each game rated vs. that opponent's usual numbers, leaving out games between the two teams. No shrinkage yet.
  - **Home/road splits** blended with weight gp/(gp + `HOME_ROAD_K` = 5).
- **Expected saves** = expected shots × **league** save% (~.885). Not goalie-specific (yet).
- **Lean**: goalie's expected shots ≥ `SHOT_THRESHOLD` (2) above/below league average. Direction first: + lean → overs only, − lean → unders only, middling → NO EDGE.
- **Tags**: line at/below expected → OVER (mirror UNDER); within `TARGET_SAVES` (1) save on the wrong side → LEAN OVER/UNDER; else NO EDGE. Internally NO EDGE is stored as tag `FADE`.
- **🔥**: OVER/UNDER only, expected ≥ `FIRE_GAP` (2.0) saves past the line, H2H avg agrees vs league avg, and raw rank top/bottom `FIRE_RANK` (10) agrees (opp shots-for or own shots-against).
- Context shown but not in the math: H2H last 4 (`H2H_GAMES`, up to 3 seasons), last 5 games for/against (`RECENT_GAMES`, comma-separated), raw ranks.

## Alert format (owner-approved — don't change without asking)
```
Markstrom (FLA) - FLA@BUF 1:10PM
DK 23.5 UNDER · FD not yet
24.6 shots, 21.9 saves expected
H2H L4 BUF on FLA @39, @20, 23, 31 (avg 28.2)
H2H L4 FLA on BUF 29, 42, @32, @32 (avg 33.8)
BUF L5 For: 24UTA, 26DAL, 28MIN, 28CHI, 26@CBJ (15th least 26.4)
FLA L5 Against: 29MIN, 20@LAK, 20@ANA, 32@SJS, 15@CAR (5th least 23.2)
FLA out: Marchand 2.6 SOG/g · SF w/ 30.5 (2), w/o 25.3 (3)
```
- One message per goalie (so replies map to one goalie). H2H only on the first goalie of a game, written `H2H L4 BUF on FLA @39, ...` (shooter on goalie; `@` = shooting team on the road). Key-player injury lines (if any) go last. `@` = that team was on the road. Day name only if the game isn't today.
- Second book posting later: `Markstrom (FLA) 24.5 UNDER · 1:10PM (FD added)`.
- Morning summary (after 7 AM ET): per-goalie results, `Season:` records per tag + 🔥 + `NO EDGE xx% over xx% under (n)`, then **Your bets** and **Your season** when he's logged bets.

## Injuries (stage 1 + 2 built Oct 12; stage 3 pending)
- Key players only: top `KEY_SHOOTERS` (3) by SOG/GP and top `KEY_DEFENSE` (2) D by TOI, this + last season with the team, current roster, ≥ `KEY_MIN_GP` (5). Owner explicitly does NOT want depth-player noise.
- Source: ESPN `site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries` (unofficial, free, every run). NHL `club-stats`, `roster`, `player/{id}/game-log` for keys and with/without. All 32 teams tracked so NEW = changed today; a team's first look seeds silently.
- One line per key player at the bottom of the alert, only when out/DTD: `FLA out: Marchand 2.6 SOG/g · SF w/ 30.5 (2), w/o 25.3 (3)`; w/ & w/o once ≥2 games missed and played.
- Change alert only when a key player goes newly OUT for an already-alerted game today before puck drop. DTD never pings.
- `picks.csv` `key_out` column logs who was out at alert time (stage 2 measurement).
- **Stage 3 (not built, needs his OK after data):** shadow injury-adjusted expected shots, e.g. shooter out → team shots −(his SOG/g − ~1.2 replacement); D effect later.
- Can't reach NHL/ESPN from Claude's workspace (proxy); test feeds via a temporary workflow that prints `::notice::` annotations (read with `gh api .../check-runs/{job}/annotations`), then delete it.

## Rechecks / credits (paid-plan settings)
- Empty games checked every run (free). Partly posted games: every `RECHECK_MINUTES` (15) while a lean goalie is missing; every `NOLEAN_RECHECK_MINUTES` (15) if only no-lean goalies are missing; within `RECHECK_WINDOW_HOURS` (10) of puck drop.
- Final checks at `FINAL_CHECKS = (45, 20)` minutes before puck drop for any incomplete game.
- Rechecks pause at `RECHECK_RESERVE`; everything pauses below `MIN_CREDITS` (20).
- **If he goes back to the free 500-credit plan:** set `NOLEAN_RECHECK_MINUTES = 180` in the script, and variables `RECHECK_MINUTES=60`, `RECHECK_RESERVE=150`. Remind him before the plan renews (~Nov 10).

## Logging his bets (Telegram)
- Swipe-reply `in` on an alert (options: `DK`/`FD`, `o`/`u`, a line, `out`), or type `I took Jarry 23u, Fowler 22o, Ellis 23 and 25o` (also `in …` / `took …`). Whole numbers mean the .5 line. Line picks the book. Bot 👍s swipe replies, replies with "Logged: …" for typed ones.
- Stored in `picks.csv` columns `taken`, `taken_line`, `taken_result`, `taken_at`; graded against the line he took.
- Logged so far: Oct 10 — Jarry u23.5 W, Fowler o22.5 W, Ellis o23.5 W, Ellis o25.5 W, Vejmelka u24.5 W, Binnington o24.5 L. Gibson u24.5 (Oct 9, W) still to be sent by him. Earlier bets (Oct 7: 2–2, Oct 8: 4–2–1, Talbot o24 Oct 9) predate logging.

## Pending / ideas (nothing built without his OK)
- **Wed Oct 14, 10 AM ET: accuracy analysis** (scheduled in the original thread). Expected vs actual saves (bias, MAE), shots error vs save% luck, by tag/home-road/lean; retro-test (1) shrinking small samples toward league avg (K≈4) — the Ellis/Buffalo case, (2) goalie-specific save% (last season, this season, blend); line-vs-actual; did the final checks catch anything; credit burn rate. Present findings, build nothing until approved.
- Observed early: NO EDGE lines went 37% over / 63% under (n=30, Oct 10). Watch it.
- More bot commands offered: `record`, `today`, `credits`, `check <name>` (1 credit), `note <name> …`.
- Longer term: injury stage 3 (math), recent form (once ~8–10 GP), game script/moneyline, line-move alerts, best parlay pair, friend via Telegram group, letting H2H nudge expected saves.

## Known limits
- Late-posted goalies can still be missed if a book posts after the last check (Talbot Oct 9, Bussi Oct 10 never appeared in the feed).
- Alerts depend on The Odds API carrying the market for that goalie.
- A goalie not on the NHL roster feed (fresh call-up) gets no team/tag.
