# SCALE v1 — fixed scoring contract

Все формулы реализованы в `scripts/analyze.py` и зафиксированы. Изменение любой константы =
новая версия шкалы (v2, v3...) и несравнимость со старыми результатами. / All formulas are
implemented in `scripts/analyze.py` and frozen. Changing any constant = a new scale version.

## Corpus

- Only user messages: `type=user`, `message.role=user`, not `isMeta`, tool results and
  synthetic wrappers (`<command-name>`, `<local-command-stdout>`, `<task-notification>`,
  `<ci-monitor-event>`, `Caveat:`, interruption stubs, continuation summaries) excluded.
- Deduplicated by `uuid` and by normalized text.
- **Voice** subset = messages ≤ 60 words without code blocks (```) and URLs — the user's
  actual typed commands, unpolluted by pasted specs/logs.
- Subagent transcripts (`agent-*.jsonl`) and `journal.jsonl` are excluded.

## Stats (0–100 each)

| Stat | Meaning | Formula (clamped to 0–100) |
|------|---------|----------------------------|
| STR — Сила / Strength | Directiveness | imperatives per 100 voice messages × 2 |
| DEX — Ловкость / Dexterity | Iteration tempo | % of voice messages ≤ 12 words × 1.4 |
| CON — Выносливость / Constitution | Intensity | 0.35 × min(100, messages per active day) + 0.35 × (% active days in span) + 0.30 × min(100, night share % × 2.5) |
| INT — Интеллект / Intelligence | Context richness | 0.4 × min(100, median words per message × 2.5) + 0.4 × min(100, % messages ≥ 100 words × 20) + 0.2 × min(100, % messages with code/URL × 5) |
| WIS — Мудрость / Wisdom | Verification & reflection | 0.5 × min(100, verify % × 6) + 0.25 × min(100, self-correction % × 25) + 0.25 × min(100, why-questions % × 8) |
| CHA — Харизма / Charisma | Diplomacy | clamp(50 + politeness % × 10 + praise % × 5 − insults % × 2 − profanity per 1000 words × 0.5) |

**RAGE — Ярость / Fury** (bonus meter, not a stat): min(100, profanity per 1000 words × 1.5
+ CAPS-messages % + multi-punctuation % ). Night share uses local-time hours 00:00–05:59.

## Level

`level = floor(sqrt(total user words) / 5)`, min 1, cap 99.
(10k words ≈ 20, 62.5k ≈ 50, 245k ≈ 99.)

## Reliability

- < 30 messages → no profile (`error: not_enough_data`).
- < 100 messages → profile marked `low_confidence: true`; the card must show a caveat.

## Marker lexicons (RU/EN)

Regex lexicons are embedded in `analyze.py` (`LEX` dict): imperatives, verify,
self-correction, politeness, praise, profanity, insults, why-questions, memory/rules,
categorical statements, Cyrillic/Latin CAPS, multi-punctuation (`???`/`!!!`), questions,
structured input. Language mix is measured on the voice subset (pasted code would skew it).
Extending a lexicon without changing formulas is still a scale bump (it shifts rates):
any lexicon edit = new scale version.
