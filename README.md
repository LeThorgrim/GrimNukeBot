# GrimNuke Bot

Personal bot made with Claude Code.

One command: `/grimnuke`.

This command deletes the channel it's run in and recreates it identically:
same name, same category, same position in the channel list, same
permissions (overwrites), same topic, same NSFW status, same slowmode (for
a text channel), or same bitrate/user limit (for a voice channel).

## 1. Create the Discord application

1. Go to https://discord.com/developers/applications
2. **New Application** → give it a name (e.g. `GrimNukeBot`)
3. **Bot** tab → **Reset Token** then copy the token (you won't be able to
   see it again afterwards)
4. Still on the **Bot** tab: no *Privileged Gateway Intent* is needed for
   this feature, you can leave everything disabled
5. **OAuth2 → URL Generator** tab:
   - Scopes: `bot` + `applications.commands`
   - Bot Permissions: `Manage Channels` (and `Send Messages` if you want
     the confirmation message in the new channel)
6. Open the generated URL at the bottom of the page and invite the bot to
   your server

## 2. Install and run the bot

```bash
cd grimnukebot
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your Discord token

python bot.py
```

On first launch, the bot syncs its slash commands (`on_ready` calls
`bot.tree.sync()`). It can take up to an hour to show up everywhere the very
first time if you don't resync manually, but in practice it's usually
near-instant on the server the bot just joined.

## 3. Usage

In any text, voice, stage, or forum channel where the bot has the
`Manage Channels` permission:

```
/grimnuke
```

Only members who themselves have the `Manage Channels` permission can use
the command (checked both on Discord's side AND in the code).

## Known limitations

- A webhook pointing to the old channel (e.g. external integrations) won't
  automatically be reconfigured to the new channel: Discord creates a
  channel with a **new ID**, this isn't an in-place reset.
- Message history is of course lost (that's the whole point of a "nuke").
- Threads from the original channel are not recreated.
- If the bot doesn't have the `Manage Channels` permission on the target
  channel, the command refuses to act rather than failing halfway through.