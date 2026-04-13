# Groq API Key Guide

AI Shadow Writer uses a bring-your-own-key model for AI generation. That means each user connects a personal Groq API key instead of sharing one global model quota.

## What A Groq API Key Is

A Groq API key is the credential that authorizes model requests through your Groq account.

In AI Shadow Writer, the key is used to:
- generate post drafts
- regenerate drafts
- revise text
- power the main AI writing workflow

## Why The Bot Uses BYOK

The product uses BYOK for a few reasons:
- users stay in control of their own AI usage
- the bot does not need to absorb hidden model costs for every user
- scaling the bot becomes simpler and more transparent
- users can manage their own Groq quota and plan

## How To Get A Groq API Key

Use the in-bot helper:

```text
/groq_help
```

That command is the product's built-in Groq onboarding entry point. If a tutorial video is configured in the bot, it can also appear there.

## How To Connect The Key

Inside the bot:

```text
/ai
```

Then paste the API key when the bot asks for it.

You can later inspect or remove the connection with:

```text
/ai_status
/ai_disconnect
```

## Common Mistakes

The most common setup issues are:
- pasting the wrong key
- pasting a truncated key
- connecting a key that is no longer valid
- assuming the bot can generate posts before `/ai` is completed

## Important Note

Your own Groq account handles your AI usage. In practical terms:
- the bot provides the workflow
- you provide the model access through your own Groq key

This is intentional and part of the product model.
