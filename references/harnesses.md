# Harnesses — где какие логи лежат и как сориентироваться

Скилл写ан для Claude Code, но идея переносима: **найди локальные логи сессий своего
харнесса, распарси реплики юзера с таймстампами — и вся аналитика ядра работает.**

**Если ты выполняешь этот скилл НЕ в Claude Code:** ниже — известные на лето 2026 места
и форматы. Если у тебя иначе (версия сменила пути, другой харнесс) — делай по аналогии:
ищи каталог данных своего харнесса, внутри — файлы сессий (обычно JSONL или JSON),
в них — записи с ролью/текстом/временем. Минимум для профиля: (role, text, timestamp,
session_id). Слои экономики/арсенала — опциональны, бери что твой формат отдаёт.

## Известные форматы (проверено дипресёрчем 2026-07-04)

| Харнесс | Путь | Формат | Что достаётся |
|---|---|---|---|
| **Claude Code** | `~/.claude/projects/<proj>/<session>.jsonl` (пропускать `agent-*.jsonl`, `journal.jsonl`) | JSONL, событие/строку: `type` = user/assistant/system/mode/pr-link/queue-operation | Всё: реплики, usage-токены (input/output/cache), tool_use, thinking, cwd, gitBranch, PR-ссылки, plan-mode |
| **Codex CLI** | `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl` (дефолт `~/.codex/sessions/`) | JSONL «роллауты»: ходы, tool calls, счётчики токенов, таймстампы | Реплики + токены + инструменты |
| **OpenCode** | `$OPENCODE_DATA_DIR` (дефолт `~/.local/share/opencode`): `message/{sessionID}/msg_*.json`, `session/{projectHash}/{sessionID}.json` | JSON-файл на сообщение + метаданные сессии | Реплики, сессии, проекты |
| **Gemini CLI** | `~/.gemini/tmp/<project_hash>/chats/` и `checkpoints/checkpoint-*.json` | JSON-дампы бесед | Реплики + tool calls; ВНИМАНИЕ: чекпоинтинг выключен по умолчанию — истории может не быть |
| **Copilot (VS Code Chat)** | `.../copilot-chat/transcripts/*.jsonl` | JSONL event-stream | Реплики чата |

Референс-имплементации парсеров: [ccusage](https://ccusage.com) (открытый код, парсит
Claude Code / Codex / OpenCode), [codex-trace](https://github.com/PixelPaw-Labs/codex-trace).
Нормализация событий разных агентов в одну схему — прецедент:
[Rivet Sandbox Agent SDK](https://rivet.dev/changelog/2026-01-28-sandbox-agent-sdk/).

## Как подключить новый источник

1. В `scripts/analyze.py` в реестр `SOURCES` добавь запись:
   `"имя": {"collect": fn(dir, project, aux) -> messages, "default_dir": "~/путь"}`.
2. `messages` — список словарей `{"text", "words", "voice", "ts", "session"}`
   (см. `collect()` Claude Code как образец: дедуп по id/тексту, фильтр синтетики,
   «voice» = ≤60 слов без код-блоков и URL).
3. `aux` — опционально: токены/инструменты/проекты, если формат отдаёт (см. `harvest()`).
4. Запуск: `python scripts/analyze.py --source имя`.

Не выдумывай форматы: если структура логов твоего харнесса неизвестна — открой один
файл сессии, посмотри глазами, потом пиши парсер.
