# Troubleshooting

This page covers common operational issues users may run into.

## Bot Is Not Responding

Check the basics first:
- the bot is still reachable in Telegram
- the hosting service is live
- the bot is not sleeping or restarting
- the deployment environment still has valid secrets configured

## Webhook and Hosting Notes

If the bot is hosted as a webhook-based service, publishing and command handling depend on:
- the public webhook URL
- a healthy running web service
- a valid Telegram webhook configuration

If hosting is down, the bot may appear silent even though the code itself is fine.

## No Admin Rights

If the bot cannot publish:
- verify it is in the channel
- verify it is an admin
- verify it has posting rights

This is one of the most common setup failures.

## Invalid Groq Key

If the connected Groq key is invalid:
- `/post` will fail
- generation cannot proceed

Reconnect the key through `/ai` if needed.

## No Channel Metadata In Forwarded Posts

Some forwarded posts do not expose enough channel information. When that happens:
- forward another post
- or use the channel ID manually

## Caption Too Long

Telegram captions have limits. If a post with a photo is too long, the bot may need to shorten or adapt the result so the media and text can still be published in a usable way.

## Photo Issues

If the photo is weak or off-topic:
- refresh the photo
- upload your own image

Do not treat automatic visual selection as final editorial output.

## Payment Issues

If access does not look correct after payment:
- check the in-bot status flow
- wait a moment for the payment event to settle
- contact support if the issue persists

For creator contact details, see [Contact](contact.md).
