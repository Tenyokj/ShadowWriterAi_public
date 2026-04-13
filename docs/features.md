# Features

AI Shadow Writer is designed as a practical Telegram workflow, not just a prompt wrapper.

## Post Generation

The `/post` command turns a short idea into a draft that is prepared for review and publication. The bot can produce both:
- creative style-based posts
- factual posts with source-aware flows when supported data is available

## Channel Memory

The bot stores reusable channel context so each generation does not start from zero. This memory includes:
- topic
- audience
- admin or author persona
- recurring content pillars
- style notes
- banned topics

This helps the bot write closer to the channel's voice over time.

## Profile Setup

The `/profile` flow collects structured channel information step by step. This is one of the main ways to improve output quality without rewriting prompts every time.

## Teach Mode

The `/teach` flow lets users forward real historical posts from the connected channel. Those samples are used as additional reference material so the bot can better match real formatting and tone.

## Photo Search

The bot can attach a visual suggestion to a generated post. The current flow prefers Pexels when configured and can also use other integrated visual search providers in the app setup.

## Own Photo Upload

If the suggested photo is not good enough, the user can upload a custom image for the draft directly in Telegram.

## Regenerate and Edit Text

Draft refinement includes two useful options:
- regenerate the draft from the same idea with a different angle or structure
- manually edit the text directly in the bot

This makes the bot useful for real editorial workflows instead of one-shot generation only.

## Publish To Channel

Once the draft is approved, the user can publish it directly to the connected channel. If a photo is attached and the caption fits Telegram limits, the bot sends the result as one combined post.

## Sources For Factual Posts

For supported factual flows, the bot can preserve source context and expose a "show sources" action so the user can inspect where important numbers came from.

This is especially useful for:
- market updates
- pricing posts
- posts where the user wants a source-backed draft rather than a purely creative one

## Bilingual Interface

The interface supports English and Russian. New users start in English by default, and can switch language with `/language`.

## Admin Panel Overview

The product also has an owner-only admin layer that can be used for runtime configuration such as:
- pricing values
- branding assets
- selected UI text fields
- basic analytics overview

This is an operational feature for the bot owner, not a shared user-facing workspace.
