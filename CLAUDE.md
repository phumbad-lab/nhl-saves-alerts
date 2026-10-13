# NHL goalie saves alerts — working notes

Read this before changing anything here. It records who this is for, how the model works,
what's been decided and why, and what's still pending. Keep it current when things change.

## The owner and how he works
- Bets NHL goalie **saves** props on DraftKings (DK) and FanDuel (FD) for fun. ~58% last year, likes 2-leg parlays. Tracks real bets in Pikkit.
- A separate "shots partner" project (shots on goal) lives in its own repo/thread. It **shares this Telegram bot and the Odds API key**. It only sends messages; only this repo reads replies (`getUpdates`). If the shots app ever starts reading replies, the two will steal each other's messages, so give it its own bot first.
- **Don't build rules on hunches.** "I don't want to build inaccurate rules." Model changes get tested against graded results first (shadow numbers, retro tests), then he approves. Never change model math without his OK.
- Cost: was strictly free; on **Oct 10 2026 he moved to the Odds API $30/month plan (20,000 credits)** for a month of tuning. See "If he goes back to free" below.
- Alert style he chose: last names, team abbreviations, ALL-CAPS tags, no odds in alerts (lines move too much; the 🔥 tells him when to act fast), short lines that are easy to search by last name.
- Explain things plainly, no jargon. He reads alerts on his iPhone (Telegram). Since Oct 12 messages are sent non-silent (`TELEGRAM_SILENT` default false) because he disliked the crossed-out bell iOS shows on silent messages; he turned the chat's sound off in Telegram instead.

## How it runs
- `saves_alert.py` runs on GitHub Actions (`.github/workflows/saves-alert.yml`), triggered **every minute** by cron-job.org (POST to the workflow_dispatch API); the built-in GitHub schedule (every 15 min, all day) is a backup. The owner pauses the cron-job.org saves job overnight (midnight–6 AM ET as of Oct 12; it was 9 AM once, which skipped the 7 AM results until a manual run). The backup was widened to all day so results go out at 7 AM regardless. If runs stop, check the cron-job.org job first. Repo is public, so Actions minutes are free.
- Secrets: `ODDS_API_KEY` (new key issued Oct 10 with the paid plan), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Variables currently set: `RECHECK_MINUTES=15`, `RECHECK_RESERVE=1000`.
- The bot commits `state.json` and `picks.csv` after runs ("Update alert state"). **Those files (and `notes.csv`) are the bot's. Never edit or commit them by hand**, and never ask the owner to upload them.
- **Pushing changes (Claude):** commit (or stash) local edits BEFORE `git pull --rebase` — a pull with a dirty tree fails and, chained with `&&`, silently skips the rest. Edit only code/docs, `git pull --rebase origin main` right before committing and pushing (the bot pushes often), `git add` the specific files only, push to `main`. Test first with the scratch harnesses (copy the script + a copy of live `picks.csv`/`state.json` into a scratch dir; never run it inside the repo, and delete `__pycache__`).
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
H2H L4 on FLA: @39, @20, 23, 31 (avg 28.2)
BUF L5 For: 24UTA, 26DAL, 28MIN, 28CHI, 26@CBJ (15th least 26.4)
FLA L5 Against: 29MIN, 20@LAK, 20@ANA, 32@SJS, 15@CAR (5th least 23.2)
INJ: Marchand LW (FLA) 2.6 SOG/g (1) · SF w/ 30.5 (2), w/o 25.3 (3)
```
- One message per goalie (so replies map to one goalie). Every full goalie alert has one H2H line for his own team: `H2H L4 on FLA: @39, @20, 23, 31 (avg 28.2)` = shots on FLA in the last 4 meetings, `@` = the shooting team was on the road (game at FLA). Owner asked for only the goalie's side (Oct 12). Key-player injury lines (if any) go last. `@` = that team was on the road. Day name only if the game isn't today.
- Labels `H2H L4 on X:`, `X L5 For:`, `X L5 Against:`, `INJ:` are underlined (owner, Oct 12): wrap with `ul()`; `send_push` switches to Telegram HTML (escaped) when a message contains `ul()` markers.
- Second book posting later: `Markstrom (FLA) 24.5 UNDER · 1:10PM (FD added)`.
- If he already bet the goalie at the first book (picks.csv `taken`) and not this one, the added line becomes `Markstrom (FLA) 24.5 UNDER 🍀 · 1:10PM (FD added) 👉 You're in DK u23.5` (one line; 🍀 after the tag only when the new number is better for his side) (owner Oct 13: he wanted a nudge, not a comparison sentence).
- **Your season** (his own record) also counts each goalie once per game: the first bet he logged on him (owner Oct 13: "I want each goalie once to see how often the reads are right"). The line shows the total bet count when it differs: `Your season: 7-2 (10 bets)`. The "Your bets" list still shows every bet.
- Season records, 🔥 record and NO EDGE split count each goalie once per game (first line alerted), not per book/line (owner, Oct 12).
- Morning summary (after 7 AM ET): one line per goalie (different lines at DK/FD listed one after another: `Markstrom (FLA) vs. BUF u23.5 UNDER (DK) ✅ · u24.5 UNDER (FD) ✅: 9 saves`), `Season:` records per tag + 🔥 + `NO EDGE xx% over xx% under (n)`, then **Your bets** and **Your season** when he's logged bets.

## Injuries (stage 1 + 2 built Oct 12; stage 3 pending)
- Key players only: top `KEY_SHOOTERS` (3) by SOG/GP and top `KEY_DEFENSE` (2) D by TOI, this + last season with the team, current roster, ≥ `KEY_MIN_GP` (5). Owner explicitly does NOT want depth-player noise.
- Source: ESPN `site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries` (unofficial, free, every run). NHL `club-stats`, `roster`, `player/{id}/game-log` for keys and with/without. All 32 teams tracked so NEW = changed today; a team's first look seeds silently.
- One line per key player at the bottom of the alert, only when out/DTD: `INJ: Marchand LW (FLA) 2.6 SOG/g (1) · SF w/ 30.5 (2), w/o 25.3 (3)`; w/ & w/o once ≥2 games missed and played. INJ = out; NEW = tonight is his first missed game, (N) = games missed in a row (from his NHL game log vs team games). Day-to-day hidden (`SHOW_GTD = False`, owner Oct 12) but still watched for change alerts.
- Change alert (`⚠️ Sanderson D (OTT) OUT - OTT@NJD 7:10PM` + affected goalie line) only when a key player goes newly OUT for an already-alerted game today before puck drop. DTD never pings.
- Back alert (`✅ Ovechkin LW (WSH) BACK - ...`, effect flipped) when a key player who was OUT comes off the ESPN list, same conditions as the change alert. OUT→DTD doesn't trigger. Feed with < `INJURY_FEED_MIN` (30) entries is treated as a bad fetch and skipped (prevents mass false BACK alerts). Owner values this for unders when a strong shooter returns.
- **Debounce (Oct 13, Bedard flapping OUT/BACK every ~2 min):** ESPN's feed is served by caches that disagree, so players blink on/off. A new OUT must hold `INJURY_CONFIRM` (5 min) before its alert (one OUT alert per absence, `alerted` flag); a player must be off the list `INJURY_CLEAR` (30 min) before he counts as back (BACK alert); status flips need 5 min too. During the grace period he's still shown as injured.
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
- `resend <name>` (or `show <name>`, or swipe-reply `resend`) rebuilds and resends a goalie's full alert from saved state (latest lines/tags/H2H/L5/injuries, no odds credit); resent messages are mapped in `state['sent']` so `in` works on them. Built Oct 12 for busy days.
- `note <name> <text>` (or swipe-reply `note ...`, or a note with no name = general thought) appends to `notes.csv` (noted_at, date, goalie, team, game, tag, line, expected_saves, note, event_id). Bot-maintained like picks.csv (workflow commits it). The daily review reads it; it's the owner's main channel for his reasoning (Oct 13).
- Nicknames: `nicknames.csv` (goalie last name, nickname; one row per nickname; 61 loaded Oct 13 from his spreadsheet) is read by `find_by_name`; a nickname may map to several goalies (most recently alerted wins) and the typed word still matches real last names. Oct 13: Hildeby = Hildy, Murashov = Mursy (changed to avoid clashes with Hill = Hilly and Matt Murray), so `in`/`took`/`note`/`resend` accept them (e.g. Wally = Wallstedt). Owner fills a spreadsheet of all 73 goalies; Claude converts it into nicknames.csv. This file is Claude-edited (not bot-maintained).
- `line <name> <number> [DK|FD]` (Oct 13, after FLA@CBJ had saves at DK but the Odds API had no `player_total_saves` market for that event): manual line → goalie found via nicknames + NHL rosters of upcoming games → inserted into `state['events'][id]['lines']` with `manual: True` (no odds) → same `alert_new_lines()` path as feed lines (alert, pick log, grading). Book defaults to DK; whole numbers → .5.
- A bet message can carry a note: `in ... note ...` / `took ... note ...` → bet logged + note saved on that goalie (Oct 13). Trailing punctuation on tokens (`24o.`, `fd.`) is ignored.
- Stored in `picks.csv` columns `taken`, `taken_line`, `taken_result`, `taken_at`; graded against the line he took.
- Logged so far: Oct 10 — Jarry u23.5 W, Fowler o22.5 W, Ellis o23.5 W, Ellis o25.5 W, Vejmelka u24.5 W, Binnington o24.5 L. Gibson u24.5 (Oct 9, W) still to be sent by him. Earlier bets (Oct 7: 2–2, Oct 8: 4–2–1, Talbot o24 Oct 9) predate logging.

## Daily review (scheduled, Oct 13)
- A scheduled task runs every morning ~7:56 AM ET (fresh session): reads last night's graded picks and judges the READ on shot volume, not just the result (right read / lucky win 🍀 e.g. goalie pulled / unlucky loss / wrong read; owner asked Oct 13 after Markstrom won an under only because he was pulled), writes 1–2 lines on *why*, keeps a read-accuracy tally, compares to the owner's own reads, and appends to `reviews.md` (patterns + owner's reads + daily entries). Purpose: collect evidence for tuning; it never changes model code.
- Owner's own reasoning: he texts `note ...` to the bot (→ `notes.csv`); the daily review folds those into `reviews.md` → "Owner's reads". If he explains a read in chat instead, add it to `reviews.md` directly.

## Pending / ideas (nothing built without his OK)
- **Wed Oct 14, 10 AM ET: accuracy analysis** (scheduled in the original thread). Expected vs actual saves (bias, MAE), shots error vs save% luck, by tag/home-road/lean; retro-test (1) shrinking small samples toward league avg (K≈4) — the Ellis/Buffalo case, (2) goalie-specific save% (last season, this season, blend); line-vs-actual; did the final checks catch anything; credit burn rate. Present findings, build nothing until approved.
- Observed early: NO EDGE lines went 37% over / 63% under (n=30, Oct 10). Watch it.
- More bot commands offered: `record`, `today`, `credits`, `check <name>` (1 credit), `note <name> …` (`resend`, `note` built).
- Longer term: injury stage 3 (math), recent form (once ~8–10 GP), game script/moneyline, line-move alerts, best parlay pair, friend via Telegram group, letting H2H nudge expected saves.

## Known limits
- The Odds API sometimes lacks the saves market for a game the books have posted (FLA@CBJ Oct 13: DK had shots/points props but no saves in the feed). Workaround: `line` command.
- Late-posted goalies can still be missed if a book posts after the last check (Talbot Oct 9, Bussi Oct 10 never appeared in the feed).
- Alerts depend on The Odds API carrying the market for that goalie.
- A goalie not on the NHL roster feed (fresh call-up) gets no team/tag.
