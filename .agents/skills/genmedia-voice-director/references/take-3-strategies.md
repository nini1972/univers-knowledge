# "Take 3 on the Bounce" Strategies (Gemini 3.8 TTS)

In voiceover work, "doing it on the bounce" means generating multiple distinct takes of the same line. With `gemini-3.8-flash-tts`, keep spoken `text` strictly verbatim (using `<short pause>`, `<sigh>`, `<laugh>` where appropriate) and drive each variation via `annotations: [{"type": "speech_metadata", "style": "..."}]` across separate `content` items or separate API calls.

## Approach 1: The "Safety" Set
Use when the core emotion is right and you want slight variations in polish or pacing.

* **Take 1 (The Direct Read):** `style: "clear, warm, straightforward corporate delivery"`
* **Take 2 (The Tweak):** `style: "warm and upbeat, slight emphasis on key innovation words"`
* **Take 3 (The Safe Option):** `style: "measured, slower, polished broadcast delivery"`

**Structured `content` Example:**
```json
[
  {
    "type": "text",
    "text": "Welcome to the future of cloud computing. We are excited to have you here. <short pause>",
    "annotations": [{ "type": "speech_metadata", "style": "clear, warm, straightforward delivery" }]
  },
  {
    "type": "text",
    "text": "Welcome to the future of cloud computing. <short pause> We are excited to have you here. <short pause>",
    "annotations": [{ "type": "speech_metadata", "style": "warm and enthusiastic, upbeat emphasis" }]
  },
  {
    "type": "text",
    "text": "Welcome to the future of cloud computing. We are excited to have you here.",
    "annotations": [{ "type": "speech_metadata", "style": "measured, slower, polished broadcast delivery" }]
  }
]
```

## Approach 2: The Character / Emotional Shift
Use when exploring contrasting emotional readings of the same line.

* **Take 1 (Frustrated):** `text: "<sigh> I can't believe the build failed again. <short pause>"`, `style: "frustrated, tense, sharp sigh"`
* **Take 2 (Defeated & Quiet):** `text: "I can't believe the build failed again. <short pause>"`, `style: "soft whisper, defeated and exhausted"`
* **Take 3 (Sarcastic Amusement):** `text: "<laugh> Oh great, I can't believe the build failed again. Fantastic."`, `style: "dry sarcasm, amused disbelief"`

## Approach 3: The Pacing / Emphasis Variation
Use for marketing copy or commercial reads where rhythm matters.

* **Take 1 (Upbeat / Fast):** `text: "Get yours today before they're entirely sold out! <short pause>"`, `style: "fast, energetic commercial pace"`
* **Take 2 (Relaxed / Conversational):** `text: "Get yours today... <short pause> before they're entirely sold out. <short pause>"`, `style: "relaxed, warm, slower conversational tone"`
* **Take 3 (Punchy):** `text: "Get yours today! <short pause> Before they're sold out!"`, `style: "punchy, crisp articulation, confident emphasis"`
