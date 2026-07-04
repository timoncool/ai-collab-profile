# Widget — card render spec

One card, one product: a serious analytical portrait with gamified flavor woven in —
NOT a character sheet. The analytics are the substance; title, achievements and the
rage gauge are the garnish. Two render targets, same content: inline widget (if the
environment has one) and a self-contained `ai-profile.html` (always).

Language: user's conversation language (profile.json carries ru/en pairs).
Numbers verbatim from profile.json. Footer: `SCALE v1 · ai-collab-profile`.

## Card sections (in order)

1. **Header**: fun title as the headline («Неистовый Командир Терминала 89 уровня,
   Железная Длань») + corpus line (messages · words · sessions · date range ·
   messages/active day; "low confidence" ribbon if flagged). No avatars, no icons,
   no badges in the header — the title carries the flavor.
2. **Volume** — metric tiles: words/message, median message length, share of ≤12-word
   quick commands, share of 200+ word specs.
3. **Top imperatives** — horizontal bars from `metrics` (imperatives rate) and the
   flavor of the user's most-used command stems if available.
4. **Tone markers** — bars with % of messages: verify, profanity, CAPS, multi-punct,
   politeness, praise, insults, self-correction. Facts, not judgment.
5. **Activity by hour** — 24 thin columns, night hours highlighted.
6. **Rage gauge** — a thin green→red bar («градус ярости») with a one-line fun caption.
   No stat blocks, no D&D strips anywhere on the card.
7. **Achievements** — one row of small chips with rarity colors (common #9aa0a6,
   rare #3b82f6, epic #a855f7, legendary #f59e0b). Earned only.
8. **Strengths / weaknesses** — 2-3 bullets each, derived strictly from the numbers
   (e.g. "проверь — второй по частоте императив" / "негатив:похвала 24:1").
9. **Recommendations** — 3-6 one-liners from references/recommendations.md (details
   go in the chat message).
10. **Footer**: `SCALE v1 · ai-collab-profile · github.com/timoncool/ai-collab-profile`.

## Images — hard rules

The card contains NO images: no avatars, no icons, no letter-SVGs, no placeholder art.
Retyping base64 blobs through the model is FORBIDDEN (corrupts bytes). Uploading any
user artifact anywhere (repos, CDNs, hosting) is FORBIDDEN.

## HTML skeleton

Dark card 760px, system fonts, no frameworks, no external resources, total file < 60 KB.
Bars = div fills, hours = flex columns, chips = inline-block. Rarity colors above;
single accent #8b5cf6 for analytic bars so the data reads calm; RAGE bar gradient
green→red.
