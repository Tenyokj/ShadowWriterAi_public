# FAQ

## Why Can't The Bot Publish To My Channel?

The most common reason is permissions. The bot must:
- be added to the channel
- be an admin
- have permission to publish posts

## Why Does `/post` Not Work?

Usually one of these is missing:
- no Groq API key connected
- no connected channel
- no remaining free access and no active paid access

Start with:
- `/ai`
- `/connect`
- `/status`

## Why Does `/connect` Fail?

The forwarded post may not contain usable channel metadata, or the bot may not have the required rights in the target channel. If forwarding does not work, try sending the channel ID manually.

## Why Is The Photo Irrelevant?

Automatic photo selection is a helper, not perfect editorial judgment. If the first result is weak, use:
- another photo
- your own uploaded image

## Why Does The Writing Style Feel Weak?

The bot performs best when the setup is complete. Make sure you have:
- filled in `/profile`
- added sample posts through `/teach`

Without that, drafts can feel more generic.

## Why Does The Bot Ask For A Groq Key?

The product uses a BYOK model for AI generation. Users connect their own Groq API key so the bot does not depend on a single shared model quota.

## Why Did The Free Limit End?

The bot includes free usage limits and may also include cooldown and anti-abuse restrictions. Once free access is used up, continued access requires a Telegram Stars plan.

## How Do I Switch Language?

Use:

```text
/language en
/language ru
```

## How Do I Contact The Creator?

See [Contact](contact.md) for the current support links and creator details.
