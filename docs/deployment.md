# Deployment

This page describes the current high-level deployment model for AI Shadow Writer.

## Deployment Overview

The product is split into a few practical parts:
- Telegram bot runtime
- PostgreSQL database
- environment-based secret configuration

## Render As Bot Hosting

The bot runtime can be deployed as a Render web service. This works well with webhook mode because the application exposes HTTP endpoints and receives Telegram updates through a public URL.

Typical production setup includes:
- a Render web service
- webhook mode enabled
- environment variables configured in the host panel

## Supabase As PostgreSQL

Supabase can be used as the managed PostgreSQL backend. The bot connects through `DATABASE_URL` and stores runtime state there.

## Webhook Mode

Hosted deployment should use webhook mode rather than local-style polling.

At a high level this requires:
- a public base URL
- a webhook path
- a webhook secret

The bot then builds the final webhook endpoint from those values.

## Environment Variable Categories

Keep production environment variables grouped conceptually:

### Core Runtime
- Telegram bot token
- application environment
- webhook settings

### Database
- PostgreSQL connection URL

### Security
- master encryption key
- webhook secret

### AI and Integrations
- Groq configuration
- photo provider API keys

### Product Settings
- free usage values
- payment plan settings
- admin user ID

## Security Notes

Production deployment should always follow these rules:
- never commit production secrets
- never expose private tokens in a public repository
- rotate compromised keys immediately
- keep runtime secrets in the hosting platform's environment manager

## Important Reminder

This documentation describes the deployment model at a high level. It should not be treated as a dump of internal infrastructure details or a source of real secret values.
