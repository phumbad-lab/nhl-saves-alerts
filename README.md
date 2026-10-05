# NHL goalie saves alerts

Checks DraftKings and FanDuel every 20 minutes (10 AM – 10 PM Eastern). The first time each book posts goalie saves lines for a game, your own Telegram bot sends you a message. Unread alerts show as a red badge number on the Telegram app icon.

Example alert:

```
FanDuel: goalie saves posted
Boston Bruins @ Detroit Red Wings · Mon 7 PM
Cam Talbot: O/U 26.5 (-115/-105) | DK 26.5
Jeremy Swayman: O/U 27.5 (-110/-110) | DK 28.5
```

When the second book posts, the alert shows the first book's line next to it so you can spot the better number.

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

## Good to know
- **Credits:** each game costs about 1 credit per book, and only once the line is posted. Checks that find nothing are free. A full NHL slate is roughly 350–400 credits a month for both books, which fits the free 500. If you get close, the script pauses itself and messages you once. Setting `TEAMS` stretches it a lot.
- **Timing:** GitHub sometimes runs scheduled jobs a few minutes late, so expect alerts within ~20–30 minutes of a line posting.
- **Free usage:** about 1,100 GitHub Actions minutes a month, inside the 2,000 free minutes for private repos.
- **Coverage:** alerts depend on The Odds API carrying the market. If a book posts saves for a goalie it doesn't cover, you won't get that one.
- **Turn it off:** Actions tab → Goalie saves alerts → "⋯" → Disable workflow.
