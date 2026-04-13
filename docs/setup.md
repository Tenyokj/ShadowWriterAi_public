# Setup Guide

This guide covers the standard first-time setup flow for a new user.

## Before You Start

Make sure you have:
- a Telegram account
- a Telegram channel you control
- permission to add the bot as an admin in that channel
- a Groq API key, or access to create one

## Step 1: Start The Bot

Open the bot in Telegram and run:

```text
/start
```

Then review:
- `/help`
- `/setup`
- `/groq_help`

## Step 2: Connect Your Groq API Key

Run:

```text
/ai
```

If you do not already have a Groq API key, open:

```text
/groq_help
```

The bot uses a BYOK model, so AI generation runs through the user's own Groq account.

## Step 3: Add The Bot To Your Channel

Before using `/connect`, add the bot to your Telegram channel as an administrator.

Important:
- the bot must be an admin in the channel
- the bot must have permission to publish posts

Without those rights, the bot may generate drafts but will not be able to publish them to the channel.

## Step 4: Connect The Channel

Run:

```text
/connect
```

Then either:
- forward any post from the channel to the bot
- or send the `channel_id` manually in the `-1001234567890` format

## Step 5: Fill The Channel Profile

Run:

```text
/profile
```

This step is strongly recommended. It gives the bot structured context about:
- what the channel is about
- who it is for
- how the author sounds
- what themes belong in the channel

## Step 6: Teach The Bot With Real Posts

Optional but recommended:

```text
/teach
```

Forward several older posts from the connected channel. This helps the bot learn the real style rather than relying only on abstract profile inputs.

## Step 7: Generate Your First Post

Run:

```text
/post your idea here
```

Then use the draft actions to:
- publish
- edit the text
- regenerate
- refresh the photo
- upload your own photo

## Important Setup Checklist

Before expecting full functionality, verify all of the following:
- the bot is started
- a Groq API key is connected
- the bot is an admin in the Telegram channel
- the bot has publishing rights
- the channel is connected
- the profile is filled in
- optional real samples were added through `/teach`

If one of these steps is missing, the bot may still respond, but the workflow will be incomplete.
