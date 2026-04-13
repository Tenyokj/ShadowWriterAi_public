# Overview

AI Shadow Writer is a Telegram bot built for channel admins who want an AI writing workflow that feels operational rather than experimental.

Instead of asking users to manage prompts manually every time, the bot keeps reusable channel context, supports guided setup, and lets users move from idea to published post inside Telegram.

## What The Bot Does

At a high level, the bot helps with four things:
- understanding the channel's topic, tone, and audience
- generating post drafts from a short idea or brief
- helping users adjust text and visuals before publishing
- sending the approved result directly to the connected Telegram channel

## Main Use Cases

Typical use cases include:
- a personal brand channel that needs consistent writing tone
- a niche media channel that needs faster drafts and visual support
- a community or market channel that needs frequent factual or promotional posts
- a creator who wants structure, but still wants final editorial control

## High-Level Product Flow

The normal flow looks like this:

1. The user starts the bot and reads the setup instructions.
2. The user connects a personal Groq API key.
3. The user adds the bot to a Telegram channel as an admin.
4. The user connects that channel to the bot.
5. The user fills in channel profile fields such as audience and author voice.
6. The user optionally teaches the bot with real sample posts.
7. The user generates a draft with `/post`.
8. The user edits, regenerates, or changes the photo if needed.
9. The user publishes the final post to the connected channel.

## Typical User Journey

The most common journey is:
- first-time setup
- AI key connection
- channel connection
- profile setup
- first draft
- ongoing usage with saved context

Once the setup is done, daily usage usually becomes much simpler:
- write an idea
- review the draft
- make a few changes
- publish

## Why The Workflow Matters

The product is designed to reduce two common problems:
- generic AI writing that does not sound like the channel
- broken publishing workflows where AI output exists, but still has to be copied and rebuilt manually

AI Shadow Writer tries to solve both by combining channel memory, draft refinement, visual support, and publishing in one Telegram-native flow.
