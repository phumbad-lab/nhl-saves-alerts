# NHL goalie saves alerts

Checks DraftKings and FanDuel every 5 minutes (via cron-job.org). When a book posts a goalie saves line, your own Telegram bot sends you a message. Unread alerts show as a red badge number on the Telegram app icon.

Example alert (first time a goalie posts):

```
Kuemper (LAK) - LAK @ VGK · Sat 10:10 PM
DK 26.5 OVER · FD not yet
30.9 shots, 27.3 saves expected
H2H L4: on LAK 25, 22, 27, 35 (avg 27.2)
H2H L4: on VGK 19, 33, 24, 26 (avg 25.5)
VGK L4 For: 43-TOR 28-SEA 28-VAN 30-ANA (3rd most 33.2)
LAK L3 Against: 30-FLA 25-SJS 29-COL (15th most 28.0)
```

- **Book line** = each book's line and its tag. 🔥 follows the tag when it qualifies (`OVER 🔥`). Odds aren't shown.
- **Shots/saves expected** = for this goalie tonight (opponent-adjusted, home/road blended).
- **H2H L4** = shots each team's goalie faced in their last four meetings, newest first (regular season and playoffs, up to three seasons back). Shown once per game, for context only.
- **L4 For / L4 Against** = the opponent's shots in each of its last four games and this goalie's team's shots allowed in each of its last four, newest first, with the opponent for each game (raw numbers). In parentheses: the league rank from raw season numbers ("most" for the top half, "least" for the bottom half) and the per-game average. A team with fewer than four games shows what it has (L3, etc.). To change the count, edit `RECENT_GAMES = 4` in `saves_alert.py`.
- The second goalie in a game gets the same block (without H2H) when he posts.
- When the other book posts a goalie you've already been alerted on, you get one line:
  `FD added: Kuemper (LAK) vs. VGK 26.5 OVER`

Everything here is free.

---

## Setup (about 15 minutes, one time)

### 1. Get an odds API key
1. Go to **the-odds-api.com** and pick the free **Starter** plan (500 credits/month).
2. The key arrives by email. Keep it handy.

### 2. Create your Telegram bot (on your iPhone)
1. Install **Telegram** from the App Store and sign up with your phone number.
2. In Telegram's search bar, search for **@BotFather** (the official one has a blue checkmark) and open it.
3. Tap **Start**, then send: `/newbot`
4. It asks for a **name**. Send something like `Saves Alerts`.
5. It asks for a **username**, which must end in `bot` and be unique. Try something like `yourname_saves_bot`.
6. BotFather replies with a **token** that looks like `8123456789:AAH...xyz`. Copy it. This is your **bot token**. Keep it private, because anyone with it can control your bot.
7. Tap the link to your new bot in that message (`t.me/yourname_saves_bot`), tap **Start**, and send it any message, like `hi`. **This step matters:** a bot can't message you until you've messaged it first.

### 3. Find your chat ID
1. In a web browser, open this address, replacing `YOUR_TOKEN` with your bot token:
   `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
   (Keep the word `bot` directly before the token, with no space.)
2. You'll see some text. Find `"chat":{"id":` followed by a number, for example `"chat":{"id":512345678,`. That number is your **chat ID**.
3. If the page shows only `{"ok":true,"result":[]}`, send your bot another message and refresh.

### 4. Put the code on GitHub (free)
1. Create a free account at **github.com** if you don't have one.
2. Create a **new private repository** named `nhl-saves-alerts`.
3. Upload the files from this folder, keeping the folder structure:
   - `saves_alert.py`
   - `state.json`
   - `README.md`
   - `.github/workflows/saves-alert.yml`

   Tip: the `.github` folder is hidden on Macs. On GitHub you can instead click **Add file → Create new file**, type `.github/workflows/saves-alert.yml` as the name, and paste in the contents.

### 5. Add your keys as secrets
In the repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add these three:

| Name | Value |
|---|---|
| `ODDS_API_KEY` | your Odds API key |
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | the number from step 3 |

### 6. Send a test
1. Go to the repo's **Actions** tab (click "enable workflows" if asked).
2. Click **Goalie saves alerts → Run workflow**, tick **test_push**, and run it.
3. Within a minute your bot should message you saying the test worked.

### 7. Make it badge-only (no pop-ups)
Choose one:

- **If you don't otherwise use Telegram:** go to iPhone **Settings → Notifications → Telegram**, turn **off** Lock Screen, Notification Center and Banners, and leave **Badges** on. Alerts then only add to the red number on the icon.
- **If you use Telegram for chatting too:** open the chat with your bot, tap its name at the top, and tap **Mute → Mute forever**. Then in Telegram go to **Settings → Notifications and Sounds** and turn on **Include muted chats** under Badge Counter, so the bot's unread alerts still count toward the badge. Your other chats keep their normal notifications.

That's it. It now runs on its own.

---

## Options
Set these under **Settings → Secrets and variables → Actions → Variables tab** (not secrets):

| Variable | What it does |
|---|---|
| `TEAMS` | Only watch certain teams, comma-separated: `Red Wings,Rangers,Bruins`. Leave unset to watch every game. |
| `TELEGRAM_SILENT` | `true` (default) delivers alerts without sound. `false` uses normal sound. |
| `SHOT_THRESHOLD` | Only watch games where a goalie's expected shots differ from the league average by at least this much. Default `2`. Set `0` to watch every game. |
| `TARGET_SAVES` | Size of the lean zone in saves. Default `1`. |
| `RECHECK_MINUTES` | How often to recheck a game where some goalies are posted but not all. Default `60`. |
| `RECHECK_WINDOW_HOURS` | Only recheck games starting within this many hours. Default `10`. |
| `RECHECK_RESERVE` | Stop rechecks (but keep first-goalie alerts) when credits drop to this. Default `150`. |

## Which games are watched
Using this season's NHL team stats (free, refreshed every 6 hours), each goalie gets:

- Team numbers are **opponent-adjusted**: each game a team plays is rated against what that opponent usually shoots or allows (leaving out its games against this team). A team that has faced weak shooters doesn't look like an elite defense, and one that has faced strong shooters isn't punished as hard.
- **expected shots** = (opponent's shots for per game + own team's shots against per game) ÷ 2, using **home/road splits**: the home goalie uses the opponent's road shooting and his team's home defense, and vice versa.
  - Splits are blended with each team's overall numbers and trusted more as games pile up: weight = split games ÷ (split games + 5). That's 17% after 1 game, 50% after 5 and 67% after 10. To change how fast splits take over, edit `HOME_ROAD_K = 5` near the top of `saves_alert.py` (lower = sooner).
- **expected saves** = expected shots × the league's save percentage

Every game is watched. A goalie has a **lean** when his expected shots are `SHOT_THRESHOLD` (default 2) or more above or below the league average; games where neither goalie has a lean are listed in each run's log as `Middling matchup` and their lines are tagged NO EDGE.

Each goalie is matched to his team using NHL rosters. **The matchup picks the direction, and the line picks the strength:**

| Goalie's expected shots | Line vs his expected saves | Tag |
|---|---|---|
| **+2 or more** vs average (overs only) | at or below expected | **OVER** |
| | up to 1 save above | **LEAN OVER** |
| | more than 1 above | **NO EDGE**, never an under |
| **−2 or more** vs average (unders only) | at or above expected | **UNDER** |
| | up to 1 save below | **LEAN UNDER** |
| | more than 1 below | **NO EDGE**, never an over |
| in between (middling) | any | **NO EDGE** |

Example: Lankinen expected 26.6 saves facing Carolina (+3.2 shots), so 26.5 is over, 27.5 is lean over and 28.5 is no edge.

If a goalie can't be matched to a team (e.g. a fresh call-up), the alert lists both teams' expected saves instead and leaves the tag off. The full math for every game is in each run's log.

## Pick log and results
Every line that gets alerted is saved to **`picks.csv`** in the repo (click it on GitHub to see it as a table): date, game, goalie, team, book, line, odds, expected saves and tag.

Each morning after 7 AM Eastern, the script pulls the previous night's NHL box scores (free), fills in **actual saves**, **outcome** (OVER / UNDER / PUSH) and **result**, and sends one Telegram message:

```
Saves results: Oct 7
Dostal (ANA) vs. EDM o25.5 OVER (DK/FD): 28 saves ✅
Levi (EDM) vs. ANA u23.5 UNDER (DK/FD): 17 saves ✅
Skinner (WPG) vs. COL 28.5 NO EDGE (DK): 25 saves → went under

Season: Over 3-0 (100%) · Lean over 1-1 (50%) · Under 2-0 (100%) · Lean under no picks yet
```

- **result:** W / L / P for over, lean over, under and lean under picks, each with its own season record. Fades are recorded with what happened (`-` in the result column) but don't count.
- **VOID:** the goalie didn't play, or the game was postponed.
- The season record counts each goalie/line once, even if both books posted it.
- The line logged is the first one seen (what you could have bet when alerted), not the closing line.

## 🔥 Fire picks
A tag gets a 🔥, as in `OVER 🔥`, only when three things agree:
1. It's an **OVER or UNDER** (never a lean) and expected saves are **2+ saves** past the line.
2. **H2H agrees**: in recent meetings, this goalie's team faced above-average shots (for an over) or below-average (for an under). No H2H means no fire.
3. **Raw ranks agree**: for an over, the opponent is top-10 in shots for or his team is top-10 in shots allowed; for an under, the bottom-10 versions.

Fire picks are marked in `picks.csv` (`fire` column) and get their own record in the morning summary (`🔥 4-1`). To adjust, search `saves_alert.py` for `FIRE_GAP = 2.0` and `FIRE_RANK = 10`.

## Rechecks (where credits go)
Checking a game with nothing posted is free, so the first goalie in every game reaches you within about 5 minutes. Once some lines are up, the game is rechecked hourly (1 credit each) **while a goalie with a lean tonight is still missing** at either book. If only no-lean goalies are missing, it's rechecked every 3 hours instead (`NOLEAN_RECHECK_MINUTES = 180` near the top of `saves_alert.py`; set 0 to never recheck them). A goalie has a lean when his expected shots are 2+ above or below average for that night's matchup. Goalies without a lean are always tagged no edge, so they get the slower schedule. If it can't tell which team a goalie plays for, it keeps rechecking to be safe. Each run's log shows how many rechecks were held back this way.

## How alerts work
Books often post one goalie early and the other hours later, so every goalie is tracked separately. You get a message each time a goalie's line appears at a book for the first time, showing both books side by side (`not yet` if one hasn't posted). A game stops being checked once both books show both goalies.

## Good to know
- **Credits:** checking a game with nothing posted is free. Any check that returns lines costs 1 credit (both books in one call). That means the first post for each game costs 1, and each hourly recheck of a partly-posted game costs 1. A full NHL slate can run past the free 500 a month. When credits fall to `RECHECK_RESERVE`, rechecks pause so first-goalie alerts keep working, and if credits fall below 20 everything pauses and you get one message. To catch every goalie all month, either set `TEAMS` or move to the $30/month plan and set `RECHECK_MINUTES` to `10` and `RECHECK_RESERVE` to `1000`.
- **Timing:** GitHub sometimes runs scheduled jobs a few minutes late, so expect alerts within ~20–30 minutes of a line posting.
- **Free usage:** about 1,100 GitHub Actions minutes a month, inside the 2,000 free minutes for private repos.
- **Coverage:** alerts depend on The Odds API carrying the market. If a book posts saves for a goalie it doesn't cover, you won't get that one.
- **Turn it off:** Actions tab → Goalie saves alerts → "⋯" → Disable workflow.
