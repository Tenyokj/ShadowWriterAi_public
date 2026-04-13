# Channel Connection

The bot must know which Telegram channel it should publish to. That is what the `/connect` flow is for.

## How `/connect` Works

Run:

```text
/connect
```

The bot then expects either:
- a forwarded post from the target channel
- or a manual channel ID in the `-100...` format

## Option 1: Connect Through A Forwarded Post

This is the simplest user flow.

1. Add the bot to the target channel as an admin.
2. Give it permission to publish posts.
3. Run `/connect`.
4. Forward any post from that channel to the bot.

If Telegram includes enough metadata in the forwarded message, the bot can extract the channel and save it.

## Option 2: Connect Through Channel ID

If forwarding is unreliable, you can send the channel ID manually.

Example format:

```text
-1001234567890
```

This is useful when:
- forwarded metadata is unavailable
- you already know the channel ID
- you want a more direct setup path

## Why The Bot Must Be A Channel Admin

Connecting a channel is not enough by itself. The bot must also be able to publish there.

That means:
- the bot must be added to the channel
- the bot must be an admin
- the bot must have posting rights

Without those rights, publishing will fail even if the connection looks correct.

## Why Forwarded Metadata Sometimes Does Not Arrive

Telegram does not always expose complete source metadata on forwarded content. This can happen because of:
- Telegram forwarding behavior
- post privacy and forwarding rules
- channel-specific forwarding limitations

When this happens, the bot may ask for another forwarded post or for the channel ID manually.

## Troubleshooting

If `/connect` does not work:
- make sure the bot is already in the channel
- make sure it has posting rights
- try forwarding a different post
- if that still fails, use the channel ID manually

If the bot previously worked with another channel, reconnecting a new channel may require updating the profile again so the stored channel memory matches the new channel.
