# Post Generation

The `/post` flow is the core writing workflow in AI Shadow Writer.

## How `/post` Works

Run:

```text
/post your idea here
```

The bot then:
- reads the connected channel context
- uses saved profile memory
- optionally uses learned channel samples
- generates a draft
- tries to attach a relevant visual
- shows a review interface before publication

## Creative Posts vs Factual Posts

The bot supports more than one generation mode.

### Creative Posts

These are style-oriented drafts where the goal is:
- tone
- structure
- persuasion
- channel fit

### Factual Posts

For some prompts, the user wants verified numbers, prices, or current facts. In those cases the bot can use factual flows and preserve supporting source context when available.

This is useful for topics like:
- market updates
- pricing
- source-backed summaries

## Regenerate

The regenerate action creates a new version from the same idea rather than starting a totally unrelated draft.

Typical use cases:
- the hook is weak
- the structure feels repetitive
- the tone is too soft or too direct
- the user wants a second angle without rewriting the prompt

## Manual Text Editing

The user can also edit the draft text manually inside Telegram. This is useful when the AI output is mostly correct but needs:
- a sharper intro
- different phrasing
- a compliance adjustment
- a final human pass before publishing

## How Photo Selection Works

The bot can fetch a photo suggestion for the draft. If the first option is not good enough, the user can:
- ask for another photo
- upload a custom image

This keeps the flow lightweight while still leaving final control to the human editor.

## How Sources Work

When the draft is based on supported factual context, the bot can preserve a list of supporting sources and expose them through the draft interface.

This is helpful when the user wants to check:
- where a number came from
- what source informed the summary
- whether the factual framing is trustworthy enough for publication

## Limitations Of Factual Mode

Factual mode is intentionally cautious.

The bot should not invent hard facts when it does not have reliable support. In unsupported cases, it may ask the user to provide:
- verified numbers
- a source excerpt
- or a different prompt

That tradeoff is intentional. It is better to stop than to publish confident nonsense.
