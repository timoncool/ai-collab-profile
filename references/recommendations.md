# Recommendations — metric-triggered, evidence-based

Правила подачи: выбрать 3–6 сработавших триггеров, подать на языке юзера, каждому совету —
короткая пометка «почему» с источником. Не морализировать. / Pick 3-6 matching entries,
deliver in the user's language, each with its evidence note. No moralizing.

Evidence base: deep-research run 2026-07-03, 45 sources, 3-vote adversarial verification
(full report: RESEARCH.md in the development repo). Key citations inline below.

## Context & task framing

**IF INT < 40 (телеграфные постановки)** → Первое сообщение задачи — самое дорогое место
для контекста: что делаем, где лежит, как поймём что готово. +10 слов контекста в старте
экономят циклы переделок дальше.
*Evidence: Anthropic prompting best practices — модель работает заметно лучше с явными
инструкциями и критериями успеха; Anthropic context engineering: контекст — конечный ресурс,
курируй его сознательно (anthropic.com/engineering/effective-context-engineering-for-ai-agents).*

**IF INT < 40 AND long_share_pct < 2** → Для крупных задач пишите спеку одним сообщением
(что/где/критерии/антипримеры) вместо серии коротких правок: длинные материалы — в начало
сообщения, сам вопрос/команду — в конец.
*Evidence: Anthropic docs — «queries at the end can improve response quality by up to 30%»
(platform.claude.com, prompting best practices).*

**IF DEX > 70 AND INT < 40** → Ваш стиль — быстрые короткие итерации. Это нормальный режим
руления, но каждая третья-четвёртая правка «не так, переделай» — сигнал, что дешевле было
дать контекст заранее. Пакуйте связанные правки в одно сообщение списком.
*Evidence: письменные навыки — значимый независимый предиктор успеха в LLM-кодинге
(preregistered study, n=100, CHI 2026, arxiv.org/pdf/2603.14133).*

## Verification & reflection

**IF WIS < 35** → Просите модель проверять свою работу явно: «прогони тесты», «покажи вывод»,
«проверь на реальных данных». Требование доказательств — самый дешёвый фильтр галлюцинаций.
*Evidence: Anthropic best practices — verification loops / evidence before claims.*

**IF verify_pct >= 10** → Ваша культура «проверь» — сильная сторона, сохраняйте её. Следующий
уровень: просить не «проверь», а «докажи выводом команды» — конкретный артефакт вместо заверения.

**IF self_correction_pct < 1** → «Стоп, я имел в виду...» — недоиспользованный инструмент:
ранняя коррекция курса на порядок дешевле доведённой до конца неверной ветки. Прерывайте сразу,
как только видите отклонение.

## Tone & emotional economy

**IF RAGE >= 60 OR insult_pct >= 10** → Фан-факт из исследований: грубость и угрозы почти
не влияют на качество ответов LLM (агрегатный эффект ≈ 0), так что ругайтесь на здоровье —
но реплика «что за говно?????» не содержит диагностики, и модель всё равно переспросит.
Экономнее сразу: что сломалось + что ожидалось.
*Evidence: threatening/tipping has no significant benchmark effect (arxiv.org/abs/2508.00614);
tone effects are narrow, small (~3%) and domain-specific (arxiv.org/html/2512.12812v1).*

**IF CHA < 20** → Вежливость сама по себе качество тоже почти не меняет — но оптимальный тон
различается по языкам (для английского лучше вежливо-прямой стиль), а позитивное подкрепление
(«это верно, продолжай») помогает модели удерживать удачное направление.
*Evidence: PLUM cross-lingual study — polite prompts improve quality up to 11% on average,
effect language- and model-dependent (arxiv.org/pdf/2604.16275; arxiv.org/abs/2402.14531).*

**IF caps_pct >= 20** → КАПС и «??????» модель понимает как усиление, но это токены без
информации. Тот же эффект даёт одно слово: «критично» или «немедленно».

## Process & sustainability

**IF memory_rules_pct >= 3** → Вы систематизируете ошибки в правила (память/скиллы/рецепты) —
это редкая и самая продуктивная привычка в корпусе. Продолжайте: каждая повторившаяся
коррекция должна становиться постоянным правилом (CLAUDE.md / skill).

**IF memory_rules_pct < 1** → Повторяете одни и те же указания? Выносите их в CLAUDE.md
или скилл — инструкция, записанная один раз, дешевле инструкции, повторённой десять раз.
*Evidence: Anthropic best practices — CLAUDE.md/skills как persistent instructions.*

**IF night_share_pct >= 30** → Треть+ вашей активности — ночью. Модели всё равно, а вот
ревью собственных мерджей стоит переносить на свежую голову: цена ошибки в 4 утра выше.

**IF neg_to_praise_ratio >= 10** → Соотношение негатив:похвала {value}:1. На качество модели
это не влияет (см. tone research) — но подтверждение «вот это правильно» информативнее
для курса, чем только сигналы об ошибках: модель узнаёт, что сохранять.

**IF max_session_messages >= 300** → Марафонские сессии копят контекст-мусор: после большого
завершённого куска дешевле начать новую сессию с коротким саммари, чем тянуть хвост.
*Evidence: Anthropic context engineering — attention budget degrades with context growth.*
