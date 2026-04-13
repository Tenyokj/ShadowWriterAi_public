<p align="center">
  <img src="docs/assets/logo-placeholder.png" alt="AI Shadow Writer logo" width="140">
</p>

<h1 align="center">AI Shadow Writer</h1>

<p align="center">
  A proprietary Telegram writing bot for channel admins who want faster drafting, stronger channel voice, and cleaner publishing workflows.
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-proprietary-black">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Telegram-2AABEE">
  <img alt="AI" src="https://img.shields.io/badge/AI-BYOK%20Groq-00A67E">
  <img alt="Database" src="https://img.shields.io/badge/database-PostgreSQL%20%2F%20Supabase-3ECF8E">
  <img alt="Hosting" src="https://img.shields.io/badge/hosting-Render-7B61FF">
  <img alt="Docs" src="https://img.shields.io/badge/docs-ready-1F2937">
</p>

> Replace `docs/assets/logo.png` with your real logo asset or external logo URL when the branding is finalized.

AI Shadow Writer is a proprietary Telegram bot for channel admins who want faster drafting, cleaner publishing workflows, and more consistent channel voice without building a custom AI stack from scratch.

The bot helps you:
- generate post drafts in your channel style
- keep channel memory such as topic, audience, and author voice
- connect your own Groq API key with a BYOK model
- review, edit, regenerate, and publish posts inside Telegram
- work with visuals, factual sources, and bilingual interface flows

## Highlights

- Telegram-native drafting and publishing workflow
- BYOK AI model through a personal Groq API key
- channel memory with profile-based context
- sample-based style improvement through `/teach`
- visual support with replace and upload flows
- factual draft support with source-aware review where available
- English and Russian interface support

## Who It Is For

AI Shadow Writer is designed for:
- Telegram channel admins
- solo creators
- niche media channels
- personal brand operators
- small editorial teams

## Why BYOK

The bot uses a bring-your-own-key model for AI generation. Each user connects a personal Groq API key through Telegram. This keeps AI usage under the user's control and avoids hiding model costs inside the bot itself.

## Quick Start

1. Open the bot in Telegram and run `/start`.
2. Use `/groq_help` if you need help creating a Groq API key.
3. Connect your key with `/ai`.
4. Add the bot to your channel as an admin with publishing rights.
5. Connect the channel with `/connect`.
6. Fill channel memory with `/profile`.
7. Optionally improve style fit with `/teach`.
8. Generate your first draft with `/post your idea`.

## Documentation

- [Documentation Home](docs/index.md)
- [Overview](docs/overview.md)
- [Features](docs/features.md)
- [Setup Guide](docs/setup.md)
- [Groq API Key Guide](docs/groq-key.md)
- [Channel Connection](docs/channel-connection.md)
- [Post Generation](docs/post-generation.md)
- [Payments](docs/payments.md)
- [Privacy](docs/privacy.md)
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [License Notes](docs/license.md)
- [Contact](docs/contact.md)

## Public Docs Note

This repository contains the private product codebase. The documentation structure included here is suitable for extraction into a separate public documentation repository later.

## License

AI Shadow Writer is proprietary software. The source code is not open source and is not licensed for public reuse, redistribution, or derivative deployment. See [LICENSE](LICENSE).
