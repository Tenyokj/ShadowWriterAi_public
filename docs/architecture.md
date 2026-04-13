# Architecture

This page gives a high-level technical overview of AI Shadow Writer without exposing internal secrets or private implementation details.

## Core Layers

The product is built around a few main layers:
- Telegram bot application layer
- persistent storage layer
- AI integration layer
- deployment and hosting layer

## Telegram Bot

The main user interface is a Telegram bot. Users interact with the product through:
- slash commands
- guided setup flows
- inline draft actions
- Telegram-native publishing behavior

## PostgreSQL and Supabase

Persistent data is stored in PostgreSQL. In the current deployment model, Supabase is used as the managed PostgreSQL provider.

This supports:
- user state
- channel connections
- channel memory
- subscriptions and access state
- analytics and runtime settings

## Render Hosting

The bot runtime can be deployed as a web service. In the current production-oriented setup, Render is used to host the bot process.

## Webhook Mode

For hosted environments, the bot can run in webhook mode rather than long-running polling. This is more suitable for web-service deployment because Telegram sends updates directly to the configured endpoint.

## BYOK Model

AI generation uses a BYOK model:
- the user connects a Groq API key
- the bot uses that key for generation
- the workflow stays centralized while model usage stays user-owned

## External Integrations

Depending on the feature path, the product can integrate with:
- Groq
- Telegram
- Supabase/PostgreSQL
- Render
- photo providers such as Pexels or Pixabay
- selected factual and research flows when supported

## Security Notes

This page intentionally avoids:
- secret values
- private environment variables
- internal operational credentials
- code-level details that do not belong in public docs

It is meant to explain the stack, not expose the deployment.
