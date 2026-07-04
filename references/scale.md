# SCALE v1.5 — fixed scoring contract

v1.1: формулы всех метрик и индексов НЕ менялись относительно v1 (профили сравнимы);
расширен набор ачивок (24 → 41) и эпитетов (7 → 11), добавлены метрики
morning/day/weekend_share. Сравнение ачивок между v1 и v1.1 — только по общим 24.
v1.2: добавлены четыре шкалы-гейджа (производные от метрик v1, формулы заморожены):
Ярость = min(100, мат/1000слов × 1.5 + капс% + мультипункт%);
Теплота = min(100, вежливость% × 12 + похвала% × 8);
Дотошность = min(100, verify% × 6 + самокоррекция% × 10 + категоричность% × 2);
Совиность = min(100, ночная доля% × 2.2). Подписи — три бакета на шкалу (≥60 / 25–59 / <25).
v1.3: новые сигналы (формулы заморожены): interruptions_per_100 (счёт «[Request interrupted»
до фильтрации); boiling_point_median — медианный номер первой реплики с маркером ярости по
сессиям от 5 реплик + boiled_sessions_pct; werewolf_ratio — (мат ночью 00-06)/(мат днём 09-18),
только при ≥50 реплик в каждой зоне; signature_words — топ-8 частотных слов юзера вне
стоп-листа и лексиконов (порог: max(5, реплик/150)).
v1.4: слои «экономика» (usage-токены ассистента: output/fresh-input/cache-read/cache-creation,
cache_efficiency = cache_read/(input+cache_read)) и «арсенал» (tool_use-вызовы по именам,
категории: operator=Bash+PowerShell, surgeon=Edit/Write, archaeologist=Read/Grep/Glob;
mcp-доля; модели; проекты по cwd; tool-ошибки по is_error), плюс images_per_100, pr_count
(дедуп по URL), plan_mode_count. ВАЖНО: слои v1.4 считаются по всему корпусу источника и
НЕ фильтруются --days/--date (v1.4-ограничение, задокументировано).
v1.5: новые метрики (формулы заморожены): reject_openers_pct — доля реплик, открывающихся
с «нет / не так / не то / опять / снова / no / wrong / again»; double_texts_per_100 — юзер-реплики,
идущие подряд без ответа ассистента между ними (состояние на файл сессии, до дедупа);
question_types_pct — среди реплик с «?» доли содержащих «почему/зачем/why», «как/how»,
«что/какой/what/which» (могут пересекаться); code_switching_pct — доля voice-реплик с ≥2
кириллическими И ≥2 латинскими словами; weekdays — гистограмма реплик по дням недели
(пн..вс, по дате timestamp). Слои: top_mcp_servers (имя = второй сегмент
`mcp__server__tool`), top_extensions (расширение file_path из tool_use-инпутов),
subagent_spawn_calls = вызовы Agent + Task + Workflow, top_sessions (топ-3 по output-токенам,
имя = customTitle либо slug), entrypoints, versions_seen, branches_seen. Две новые шкалы:
Нетерпеливость = min(100, interruptions_per_100 × 1.5), бакеты ≥60/25–59/<25;
Кэш-скряга = cache_efficiency_pct, бакеты ≥85/50–84/<50 (только если экономика доступна).
ИСПРАВЛЕНИЕ УЧЁТА (влияет на экономику задним числом): один API-ответ пишется в JSONL
несколькими строками с одинаковым message.id — usage, счётчик ответов и модель теперь
считаются один раз на (message.id, requestId), как в ccusage. Экономика v1.4 была завышена
до ~3×; профили v1.4 и v1.5 по слою «экономика» НЕсравнимы, по метрикам v1–v1.3 — сравнимы.

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

## Behavioral indexes (0–100, internal)

Internal scores used ONLY to pick the fun rank in the title — the card shows raw metrics,
never an RPG stat sheet:

| Index | Meaning | Formula (clamped to 0–100) |
|-------|---------|----------------------------|
| command | Directiveness | imperatives per 100 voice messages × 2 |
| tempo | Iteration tempo | % of voice messages ≤ 12 words × 1.4 |
| endurance | Intensity | 0.35 × min(100, messages per active day) + 0.35 × (% active days in span) + 0.30 × min(100, night share % × 2.5) |
| context | Context richness | 0.4 × min(100, median words per message × 2.5) + 0.4 × min(100, % messages ≥ 100 words × 20) + 0.2 × min(100, % messages with code/URL × 5) |
| verification | Verification & reflection | 0.5 × min(100, verify % × 6) + 0.25 × min(100, self-correction % × 25) + 0.25 × min(100, why-questions % × 8) |
| diplomacy | Diplomacy | clamp(50 + politeness % × 10 + praise % × 5 − insults % × 2 − profanity per 1000 words × 0.5) |

Дополнительные доли времени: morning_share_pct (05:00–09:59), day_share_pct (09:00–18:59),
weekend_share_pct (суббота-воскресенье по дате реплики) — используются ачивками и эпитетами,
в индексы НЕ входят.

**Ярость / RAGE meter** (shown on the card as a fun gauge): min(100, profanity per 1000
words × 1.5 + CAPS-messages % + multi-punctuation %). Night share uses local-time hours
00:00–05:59.

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
