# Gemini 3.8 TTS Inline Vocal Tags & Style Guide

Gemini 3.8 TTS (`gemini-3.8-flash-tts` and `gemini-3.8-flash-lite-tts`) separates **point-in-time inline vocal tags** inside `text` from **sustained emotional/acting directions** inside `speech_metadata.style`.

> [!IMPORTANT]
> Do **not** embed square-bracket stage directions (like `[anger]`, `[whispers]`, or `[medium pause]`) inside `text`. In Gemini 3.8 TTS, `text` is read verbatim unless using the supported angle-bracket vocal tags below.

## Supported Inline Vocal Tags (Inside `text`)

Use angle brackets for momentary human vocalizations and pauses:

* `<laugh>` — natural laughter
* `<sigh>` — audible exhale/sigh
* `<gasp>` — sharp intake of breath / surprise
* `<cough>` — brief throat clear or cough
* `<breath>` — audible breath before a phrase
* `<short pause>` — brief rhythmic pause

Example:
```text
Wait... <short pause> did you hear that? <sigh> Let's try again.
```

## Sustained Tone, Emotion, and Pacing (Inside `speech_metadata.style`)

Move all sustained delivery adjectives into the `speech_metadata` annotation's `style` field:

* **Emotion & Attitude:** `"urgent and whispered"`, `"warm and enthusiastic"`, `"calm, reverent documentary narrator"`, `"exhausted and cynical"`, `"cheerful and friendly"`, `"sarcastic amusement"`, `"quiet awe"`
* **Pacing & Dynamics:** `"slow, deliberate pacing"`, `"fast, energetic cadence"`, `"soft, intimate whisper"`, `"firm projection"`
* **Accent:** `"Brixton London accent"`, `"Belgian Dutch (Flemish)"`, `"Received Pronunciation British English"`

Example annotation:
```json
{
  "type": "speech_metadata",
  "style": "whispered urgently, fast pacing, slight nervousness"
}
```
