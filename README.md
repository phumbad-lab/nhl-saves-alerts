# NHL goalie saves alerts

Checks DraftKings and FanDuel every 5 minutes (via cron-job.org). When a book posts a goalie saves line, your own Telegram bot sends you a message. Unread alerts show as a red badge number on the Telegram app icon.

Example alert (first time a goalie posts):

```
Saves - VAN @ CAR · Thu 7:10 PM
Kevin Lankinen (VAN) · DK 28.5 (-105/-130) (fade) · FD not yet
Exp. 25.6 saves, 29.0 shots
H2H last 4: on VAN 33, 38, 20, 32 (avg 30.8)
on CAR 22, 17, 14, 27 (avg 20.0)
CAR shots for 7th most (30.2) · VAN shots against 7th most (30.0)
```

- **Exp.** = expected saves and shots for this goalie tonight (opponent-adjusted, home/road blended).
- **H2H last 4** = shots each team's goalie faced in their last four meetings, newest first (regular season and playoffs, up to three seasons back). Shown once per game, for context only.
- **Rank line** = the opponent's shots for and this goalie's team's shots against, ranked across the league from raw season numbers ("most" for the top half, "least" for the bottom half), with the per-game average.
- The second goalie in a game gets the same block (without H2H) when he posts.
- When the other book posts a goalie you've already been alerted on, you get one line:
  `FD added - VAN @ CAR: Lankinen 27.5 (-114/-114) (fade)`

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

A game is watched only if at least one goalie's expected shots are `SHOT_THRESHOLD` (default 2) or more above or below the league average. Skipped games cost nothing and are listed in each run's log as `Skip (middling matchup)`. If the NHL stats can't be loaded, every game is watched.

Each goalie is matched to his team using NHL rosters. **The matchup picks the direction, and the line picks the strength:**

| Goalie's expected shots | Line vs his expected saves | Tag |
|---|---|---|
| **+2 or more** vs average (overs only) | at or below expected | **(over)** |
| | up to 1 save above | **(lean over)** |
| | more than 1 above | **(fade)**, never an under |
| **−2 or more** vs average (unders only) | at or above expected | **(under)** |
| | up to 1 save below | **(lean under)** |
| | more than 1 below | **(fade)**, never an over |
| in between (middling) | any | **(fade)** |

Example: Lankinen expected 26.6 saves facing Carolina (+3.2 shots), so 26.5 is over, 27.5 is lean over and 28.5 is fade.

If a goalie can't be matched to a team (e.g. a fresh call-up), the alert lists both teams' expected saves instead and leaves the tag off. The full math for every game is in each run's log.

## Pick log and results
Every line that gets alerted is saved to **`picks.csv`** in the repo (click it on GitHub to see it as a table): date, game, goalie, team, book, line, odds, expected saves and tag.

Each morning after 7 AM Eastern, the script pulls the previous night's NHL box scores (free), fills in **actual saves**, **outcome** (OVER / UNDER / PUSH) and **result**, and sends one Telegram message:

```
Saves results: Oct 7
Lukas Dostal o25.5 (DK/FD): 28 saves ✅
Devon Levi u23.5 (DK/FD): 17 saves ✅
Stuart Skinner 28.5 fade (DK): 25 saves → went under

Season: Over 3-0 (100%) · Lean over 1-1 (50%) · Under 2-0 (100%) · Lean under no picks yet
```

- **result:** W / L / P for over, lean over, under and lean under picks, each with its own season record. Fades are recorded with what happened (`-` in the result column) but don't count.
- **VOID:** the goalie didn't play, or the game was postponed.
- The season record counts each goalie/line once, even if both books posted it.
- The line logged is the first one seen (what you could have bet when alerted), not the closing line.

## Rechecks (where credits go)
Checking a game with nothing posted is free, so the first goalie in every game reaches you within about 5 minutes. Once some lines are up, the game is rechecked hourly (1 credit each), **but only while a goalie with a lean tonight is still missing** at either book. A goalie has a lean when his expected shots are 2+ above or below average for that night's matchup. Goalies without a lean are always tagged fade, so the script doesn't spend credits waiting on them. If it can't tell which team a goalie plays for, it keeps rechecking to be safe. Each run's log shows how many rechecks were skipped this way.

## How alerts work
Books often post one goalie early and the other hours later, so every goalie is tracked separately. You get a message each time a goalie's line appears at a book for the first time, showing both books side by side (`not yet` if one hasn't posted). A game stops being checked once both books show both goalies.

## Good to know
- **Credits:** checking a game with nothing posted is free. Any check that returns lines costs 1 credit (both books in one call). That means the first post for each game costs 1, and each hourly recheck of a partly-posted game costs 1. A full NHL slate can run past the free 500 a month. When credits fall to `RECHECK_RESERVE`, rechecks pause so first-goalie alerts keep working, and if credits fall below 20 everything pauses and you get one message. To catch every goalie all month, either set `TEAMS` or move to the $30/month plan and set `RECHECK_MINUTES` to `10` and `RECHECK_RESERVE` to `1000`.
- **Timing:** GitHub sometimes runs scheduled jobs a few minutes late, so expect alerts within ~20–30 minutes of a line posting.
- **Free usage:** about 1,100 GitHub Actions minutes a month, inside the 2,000 free minutes for private repos.
- **Coverage:** alerts depend on The Odds API carrying the market. If a book posts saves for a goalie it doesn't cover, you won't get that one.
- **Turn it off:** Actions tab → Goalie saves alerts → "⋯" → Disable workflow.
