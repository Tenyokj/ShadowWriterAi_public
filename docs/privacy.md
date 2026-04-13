# Privacy

This page explains the product's privacy model at a practical level.

## What The Bot Stores

The bot stores operational data needed to make the workflow function. This can include:
- Telegram user identifiers needed for bot usage
- connected channel identifiers
- channel profile memory
- generated draft metadata
- usage and subscription state
- selected configuration values

## What Channel Data Is Stored

The bot can store information about the connected channel, including:
- channel ID
- title or description when available
- structured channel profile fields
- real sample posts provided through channel activity or `/teach`

This storage exists so the bot can write closer to the real voice of the channel.

## How The Groq Key Is Stored

The user's Groq API key is not meant to be stored as plain text in the database. The product uses encrypted storage backed by a server-side master encryption key.

This means:
- the bot needs the key to operate the workflow
- the key is intended to be stored in an encrypted form
- production secrets should be handled through environment variables, not source control

## Third-Party APIs

Depending on the workflow and configuration, the bot may use third-party services such as:
- Groq for AI generation
- Telegram Bot API
- Supabase/PostgreSQL for persistence
- Render or another host for bot runtime
- visual search providers such as Pexels or Pixabay
- selected factual data or research integrations when supported

## What Is Not The Goal

The bot is not intended to become a full private archive of everything in a channel. It stores only the operational context needed for the product workflow.

## Practical Privacy Summary

In short:
- the bot stores enough data to generate, refine, and publish posts
- user AI keys are intended to be stored securely
- third-party providers are part of the workflow
- production secrets must never be committed publicly

If you need legal or enterprise-grade policy text, this page should be treated as a concise product explanation rather than formal legal counsel.
