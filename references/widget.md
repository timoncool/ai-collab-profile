# Card template — спецификация карточки

**Канонический сборщик — `scripts/render.py`.** Модель НЕ пишет HTML/CSS/SVG: она
готовит `content.json` (хроника + сильное/слабое по правилам ниже) и запускает
рендерер; всё числовое, бары, иконки, фавикон и печать он делает сам из profile.json
и assets. Этот файл — контракт того, ЧТО рендерер выводит: правила отбора текстов
для content.json, словарь подписей RU/EN, шаблон разметки (для сверки и развития
рендерера), правила инлайн-виджета и текстового фолбэка.

Одна карточка, один продукт: серьёзный аналитический портрет с геймифицированной
приправой — НЕ лист персонажа. Заполняй шаблон данными из profile.json, ничего не
выдумывая: структура, CSS и порядок секций — как ниже, слово в слово. Меняются только
данные и выбранные правилами пункты. Язык — язык общения юзера (в profile.json — ru/en).

## Язык: RU и EN — симметричные первоклассные версии

Язык карточки определяется АВТОМАТИЧЕСКИ: это язык общения юзера в текущей сессии
(попросил на другом языке — его выбор важнее). profile.json двуязычен целиком
(title/gauges/achievements/identity/imperatives несут поля ru и en) — данные НЕ переводить,
брать готовое поле нужного языка. Подписи карточки берутся из словаря ниже: колонка RU
или EN, слово в слово. «Хронику воина» модель пишет на языке карточки. «Словарь воина» —
всегда реальные слова юзера из логов, их язык не меняется. Обе версии обязаны быть
симметричны: те же секции, те же числа, тот же порядок.

### Словарь подписей (RU | EN)

| RU | EN |
|----|----|
| Хроника воина | Warrior's Chronicle |
| Объём реплик | Message volume |
| слов в среднем | words on average |
| слов, медиана | words, median |
| короткие (до 12 слов) | short (up to 12 words) |
| спеки (от 200 слов) | specs (200+ words) |
| Топ императивов | Top imperatives |
| Маркеры тона | Tone markers |
| мат / вопросы / капс, крик / оскорбления / !!!! и ???? / проверь-запросы / самокоррекция / вежливость | profanity / questions / CAPS, shouting / insults / !!!! and ???? / verify-requests / self-correction / politeness |
| Часы активности | Hours of activity |
| Дни недели (пн..вс) | Days of week (Mo..Su) |
| Шкалы | Gauges |
| Экономика и арсенал | Economy & arsenal |
| токенов сгенерировано / кэш-эффективность / вызовов инструментов / разных инструментов / проектов / PR и MR из сессий | tokens generated / cache efficiency / tool calls / distinct tools / projects / PRs and MRs shipped |
| Топ инструментов | Top tools |
| Стиль работы — вызовы по ролям | Working style — calls by role |
| Оператор — консоль: Bash, PowerShell | Operator — console: Bash, PowerShell |
| Хирург — правки кода: Edit, Write | Surgeon — code edits: Edit, Write |
| Археолог — чтение и поиск: Read, Grep | Archaeologist — reading & search: Read, Grep |
| Кукловод — MCP: внешние серверы | Puppeteer — MCP: external servers |
| Прочее — всё остальное | Other — everything else |
| MCP-парк — внешние серверы | MCP fleet — external servers |
| Файлы в работе — топ расширений | Files touched — top extensions |
| Боевые повадки | Battle habits |
| прерываний на 100 реплик | interruptions per 100 messages |
| точка кипения: реплика первой вспышки (кипит N% сессий) | boiling point: first-flare message (N% of sessions boil) |
| оборотень: ночной мат к дневному | werewolf: night profanity vs day |
| скриншотов на 100 реплик | screenshots per 100 messages |
| дабл-текстов на 100 реплик — мысли очередями | double-texts per 100 — thoughts in salvos |
| вызовов субагентов — армии по одному слову | subagent spawns — armies at a word |
| реплик открываются с «нет / не так» | messages open with "no / wrong" |
| реплик мешают RU и EN в одной фразе | messages mix RU and EN in one phrase |
| вопросов — «что», N% «как», N% «почему» | of questions ask "what", N% "how", N% "why" |
| вызовов инструментов — с ошибкой | of tool calls error out |
| ответов модели — с thinking-блоками | of replies carry thinking blocks |
| достижений открыто | achievements unlocked |
| Конюшня — ответы по моделям | The stable — replies by model |
| Сетап · вход в Claude Code · план-режим · версий Claude Code за период · самая дорогая сессия | Setup · Claude Code entrypoint · plan mode · Claude Code versions in period · most expensive session |
| Словарь воина | Warrior's vocabulary |
| Достижения · условие: | Achievements · unlock: |
| Показать все достижения — ещё N (rare и common) | Show all achievements — N more (rare & common) |
| Сильное | Strong |
| Слабое и что делать | Weak — and what to do |
| уровень · реплик · слова · сессий · реплик в активный день | level · messages · words · sessions · messages per active day |
| Понравилось? Поставьте звезду ★ | Enjoyed it? Star the repo ★ |

Имена моделей: Опус/Opus, Фейбл/Fable, Сонет/Sonnet, Хайку/Haiku + номер версии.

## Жёсткие правила (нарушение = брак)

1. **Каждое число появляется на карточке ровно один раз.** Поздние секции ссылаются
   на ранние словами («медиана — в Объёме», «см. маркеры»), не перепечатывают.
2. Замечание про исследования тона — один раз, в подписи шкалы «Ярость». Больше нигде.
2г. Роли инструментов НИКОГДА не подаются голыми словами («оператор 34%») — только бар
   с двухстрочной подписью: имя роли + пояснение, какие инструменты в неё входят.
2д. SVG-файлы из assets НИКОГДА не читать в контекст (Read по .svg запрещён — это
   тысячи символов координат впустую). Готовый инлайн-код любой иконки печатает
   `scripts/icons.py`:
   `python scripts/icons.py section scales` — иконка секции (20px);
   `python scripts/icons.py achievement tyrant legendary` — иконка ачивки (38px,
   сам падает на _<rarity>, если именной нет);
   `python scripts/icons.py favicon` — целиком <link rel="icon"> для <head>;
   `python scripts/icons.py seal` — герб для печати футера;
   `python scripts/icons.py list` — все доступные имена.
   Вызывай его из своего сборочного скрипта (import icons / subprocess), а не по
   одной иконке руками в чат.
2б-икон. Иконки секций: каждый <h2> открывается инлайн-SVG (20px, цвет наследуется
   латунный) от `scripts/icons.py section <имя>` — сами .svg не читать (2д).
   Маппинг секция→файл — в assets/section-icons/ATTRIBUTION.md.
2в. Шкалы (gauges) — ВСЕ из массива profile.gauges (v1.5: до шести — Ярость, Теплота,
   Дотошность, Совиность, Нетерпеливость, Кэш-скряга; последняя есть только при доступной
   экономике), с готовыми подписями-бакетами; не выдумывать свои формулы и тексты.
2а. Все упоминания источников (arxiv, Anthropic docs) — КЛИКАБЕЛЬНЫЕ <a href>, не голый текст.
2б. Ачивки — стим-стайл карточками (.ac) в 2 КОЛОНКИ: крупный медальон-иконка слева,
   справа название (цвет редкости) + редкость + флейвор (desc_*). Условие получения
   (cond_*) НЕ печатается на карточке — оно в ховер-подсказке .cd (появляется над
   карточкой при наведении). Сразу показываются ТОЛЬКО legendary и epic; rare и common —
   внутри <details class="more"> с summary «Показать все достижения — ещё N (rare и
   common)». Если legendary/epic нет вовсе — показать первые 6 по редкости, остальное
   в аккордеон.
3. Никаких ВНЕШНИХ ресурсов (кроме Google Fonts <link>) и никаких base64-вставок,
   набранных моделью. Локальное — можно и нужно: avatar.png (4б), SVG-иконки из assets
   (2б-икон, 4в), фавикон и печать (3а).
3а. Фавикон и печать: логотип проекта — герб «перекрещенные мечи + щит» с монограммой
   PW по центру щита (assets/swords-emblem.svg + собранный assets/logo.svg,
   game-icons/lorc, CC-BY-3.0). В <head> — data-URI SVG-фавикон: строку целиком печатает
   `python scripts/icons.py favicon` (карточка остаётся автономным файлом). В футере
   .seal — герб 32px от `python scripts/icons.py seal`. Сами .svg не читать (2д).
4. Отдельной секции «Рекомендации» НЕТ — советы живут парами в «Слабое → что делать».
4а. Идентичность: строка под титулом «{класс} · {раса} ({доля}% реплик)» из profile.identity;
   расу опускать если identity.race == null; класс есть всегда.
4б. Аватар: если рядом с карточкой есть avatar.png (scripts/avatar.py, robohash) —
   <img src="avatar.png"> слева в шапке, 150-160px, скруглённый. Файла нет — шапка без
   картинки; заглушки, буквы и иконки вместо аватара ЗАПРЕЩЕНЫ.
4в. Иконки ачивок: КРУПНО, как настоящая ачивка: медальон .aico (54px, рамка цвета
   редкости, тёмный радиальный фон) слева, внутри иконка 38px от
   `scripts/icons.py achievement <id> <rarity>` (фолбэк на _<rarity> встроен;
   game-icons.net CC-BY-3.0, атрибуция в ATTRIBUTION.md; сами .svg не читать — 2д),
   красится цветом редкости; текст справа (.atx). Карточки не растягивать по высоте
   ряда (align-items:start) — без пустот.
5. Числа — из profile.json как есть, без округлений и смягчений.
6. «Хроника воина» — секция сразу после дельта-полосы: 2-4 абзаца (~100-180 слов),
   которые МОДЕЛЬ пишет сама по profile.json (см. SKILL.md, шаг 3а): характеристика /
   мини-биография в тоне летописи с лёгким юмором. Факты только из профиля, БЕЗ чисел
   (правило №1), нейтрально к значениям метрик. Оформление: .chron с буквицей,
   1-2 акцента <em>.

## Выбор пунктов «Сильное» (до 3, в этом порядке приоритета)

- verify_pct ≥ 6 и «проверь» в топ-3 императивов → «Культура верификации реальная:
  „проверь" — в топе императивов (бары выше)»
- memory_rules_pct ≥ 3 → «Ошибки системно превращаются в постоянные правила и скиллы»
- span ≥ 14 дней и активных ≥ 70% → «Стабильность: X активных дней из Y, марафоны
  до N реплик — проекты доводятся» (эти числа встречаются только здесь)
- politeness_pct ≥ 3 и insult_pct < 5 → «Ровный уважительный тон — редкость, сохраняйте»
- long_share_pct ≥ 3 → «Умеете в спеки (доля — в Объёме)»
- question_pct ≥ 30 → «Диагностический диалог: треть реплик — вопросы»
- imperatives ≥ 30/100 и rage < 20 → «Спокойная директивность: командуете много, не повышая тона»
- long_share ≥ 8% → «Постановки-чертежи: развёрнутые спеки — ваш основной инструмент»
- day_share ≥ 55% → «Здоровый график: работа умещается в день»

## Выбор пар «Слабое → что делать» (до 4, из recommendations.md, приоритет сверху вниз)

- медиана ≤ 15 → телеграфные постановки → «+10 слов контекста в первую реплику;
  длинное — в начало, команду — в конец» · пруф: до +30% (Anthropic docs)
- neg_to_praise ≥ 10 → «N негативных сигналов на одну похвалу» (число — только здесь)
  → «подтверждайте верное направление» · пруф: тон качество не меняет (см. ярость)
- self_correction_pct < 2 → «заметили, что модель делает не то — останавливайте сразу, не ждите конца» · практика
- verify_pct < 4 → «просите артефакт: „прогони тесты и покажи вывод"» /
  verify_pct ≥ 6 → «не „проверь", а „докажи выводом команды"» · Anthropic: evidence before claims
- caps_pct ≥ 20 → «капс — токены без информации; одно слово „критично" работает так же»
- max_session ≥ 300 → «новая сессия с саммари после большого куска» · context rot (Anthropic)
- night ≥ 30% → «ревью своих мерджей — на свежую голову» · практика

Факт не может быть и сильным, и слабым одновременно (выбери одно).

## Универсальность (обязательно)

Шаблон должен давать осмысленную карточку ЛЮБОМУ юзеру, не только эмоциональному
марафонцу:
- «Сильное» пусто по правилам → одна строка: «Ровный сбалансированный стиль — без
  выраженных перекосов» (и ничего не выдумывать).
- «Слабое → что делать» собрало < 2 пар → добить универсальными: «просите артефакт
  вместо заверения» и «+контекст в первую реплику» (они полезны всем).
- Ачивок 0 → секцию скрыть целиком (не показывать пустую).
- neg_to_praise_ratio = null → пару про негатив не использовать.
- Никогда не предполагать высокий градус ярости/мата — все тексты нейтральны к
  значению метрик, кроме явно выбранных правилами.

## HTML-шаблон «Гримуар v1» (утверждён юзером: без арки, без римских цифр; заполнить {{...}})

Шрифты Google (Cormorant Garamond / Cinzel / Crimson Pro) подключать <link>-ом как в
образце; офлайн деградирует на Georgia — допустимо.

```html
<!doctype html><html lang="{{lang}}"><head><meta charset="utf-8"><title>Prompt Warrior</title><!-- data-URI фавикон, правило 3а -->
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Cormorant+SC:wght@500;600;700&family=Cinzel:wght@500;600&family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
:root{--bg:#120e0b;--card:#1C1714;--oak:#251E19;--oak2:#2B231D;--line:#4A3F35;--text:#E8DFD4;--mut:#B3A18C;--brass:#C9A962;--brass-dim:#8F7440;--crimson:#8B2635}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font:15.5px/1.6 "Crimson Pro","PT Serif",Georgia,serif;display:flex;justify-content:center;padding:28px;margin:0}
.card{width:820px;background:linear-gradient(170deg,#201A15 0%,var(--card) 22%,#191411 100%);border:1px solid #3A312A;border-radius:14px;padding:34px 40px;position:relative;
box-shadow:0 1px 0 rgba(255,255,255,.05) inset,0 -2px 0 rgba(0,0,0,.35) inset,0 2px 6px rgba(0,0,0,.5),0 18px 50px rgba(0,0,0,.55)}
.card:before{content:"";position:absolute;inset:0;border-radius:14px;pointer-events:none;z-index:2;
background:radial-gradient(120% 90% at 50% 8%,transparent 50%,rgba(0,0,0,.34) 100%),url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"/></filter><rect width="140" height="140" filter="url(%23n)" opacity="0.045"/></svg>')}
.card>*{position:relative;z-index:3}
.card:after{content:"";position:absolute;inset:10px;border:1px solid rgba(201,169,98,.22);border-radius:9px;pointer-events:none}
h1{font:600 30px/1.22 "Cormorant Garamond",Georgia,serif;margin:8px 0 3px;text-shadow:0 1px 0 rgba(0,0,0,.6)}
h2{font:600 12.5px "Cinzel","Cormorant SC",Georgia,serif;letter-spacing:.2em;text-transform:uppercase;color:var(--brass);margin:26px 0 12px;display:flex;align-items:center;gap:11px}
h2:before{content:"";width:24px;height:1px;background:linear-gradient(90deg,transparent,var(--brass-dim))}
h2:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--brass-dim),transparent 85%)}
.muted{color:var(--mut);font-size:13px}
a{color:var(--brass);text-decoration:none;border-bottom:1px dotted var(--brass-dim)}a:hover{color:#E0C685}
.head{display:flex;gap:20px;align-items:center;padding-bottom:16px;border-bottom:1px solid rgba(201,169,98,.25);position:relative}
.head img{width:156px;height:156px;border-radius:14px;border:2px solid rgba(201,169,98,.4);background:#171310;box-shadow:0 3px 10px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.1);flex:none}
.ident{font:600 13px "Cinzel","Cormorant SC",Georgia,serif;letter-spacing:.08em;color:var(--brass)}
.lvl{flex:none;text-align:center;padding:11px 13px;border:1px solid rgba(201,169,98,.4);border-radius:10px;background:linear-gradient(180deg,#2B231D,#1E1813);box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 3px 8px rgba(0,0,0,.45)}
.lvl b{display:block;font:600 22px "Cinzel","Cormorant SC",Georgia,serif;color:var(--brass);letter-spacing:.04em}
.lvl span{display:block;font-size:10px;color:var(--mut);letter-spacing:.14em;text-transform:uppercase;margin-top:2px}
.chron{font-size:15px;line-height:1.65;color:#D5C9B8}
.chron p{margin:0 0 10px}
.chron p:first-child:first-letter{font-family:"Cormorant Garamond",Georgia,serif;font-size:34px;font-weight:700;color:var(--brass);float:left;line-height:1;margin:2px 7px 0 0}
.chron em{color:var(--brass);font-style:italic}
.dstrip{margin-top:12px;padding:6px 13px;border:1px solid #3A312A;border-radius:8px;font-size:13px;color:var(--mut);background:rgba(37,30,25,.7)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
.grid6{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.tile{background:linear-gradient(180deg,var(--oak2),var(--oak));border-radius:9px;padding:11px 13px;border:1px solid #352C24;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),inset 0 -2px 4px rgba(0,0,0,.35),0 1px 2px rgba(0,0,0,.4)}
.tile b{font-size:21px;display:block;font-variant-numeric:tabular-nums;font-family:"Cormorant Garamond",Georgia,serif;font-weight:700}
.tile span{font-size:12.5px;line-height:1.45;color:#C0AF9A;display:block;margin-top:2px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:8px 32px}
.row{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.row .lb{width:130px;font-size:13.5px;color:var(--mut);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{flex:1;height:12px;background:#171310;border-radius:6px;overflow:hidden;border:1px solid #322A23;box-shadow:inset 0 2px 4px rgba(0,0,0,.55)}
.bar i{display:block;height:100%;border-radius:5px;box-shadow:inset 0 1px 0 rgba(255,255,255,.25)}
.row .vl{width:50px;font-size:13px;font-variant-numeric:tabular-nums}
.duo{display:grid;grid-template-columns:1.15fr 1fr;gap:32px;align-items:start}
.hours{display:flex;align-items:flex-end;gap:3px;height:52px;padding:6px 8px 0;background:#171310;border:1px solid #322A23;border-radius:8px;box-shadow:inset 0 2px 5px rgba(0,0,0,.5)}
.hours i{flex:1;background:linear-gradient(180deg,#5C4F41,#463B30);border-radius:2px 2px 0 0;box-shadow:inset 0 1px 0 rgba(255,255,255,.12)}
.hours i.n{background:linear-gradient(180deg,#D8B872,#A5843F);box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 0 6px rgba(201,169,98,.25)}
.growl{display:flex;align-items:center;gap:10px;margin-bottom:3px}
.glb{width:110px;font-size:13.5px;color:var(--mut);text-align:right}
.gvl{width:28px;font-size:13px;font-variant-numeric:tabular-nums}
.gauge{height:12px;border-radius:6px;border:1px solid #322A23;background:linear-gradient(90deg,#6E7F46,#A08430 45%,#9C4A26 75%,#7E2B20);box-shadow:inset 0 2px 4px rgba(0,0,0,.45);position:relative}
.needle{position:absolute;top:-4px;width:4px;height:20px;background:linear-gradient(180deg,#F0DCAC,#C9A962 60%,#8F7440);border-radius:2px;box-shadow:0 0 4px rgba(0,0,0,.6),0 0 8px rgba(201,169,98,.4)}
.gnote{font-size:12px;margin:0 30px 9px 120px;color:#A8977F}
.chips{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;align-items:start}
.ac{position:relative}
.ac .cd{visibility:hidden;opacity:0;transition:opacity .15s;position:absolute;bottom:calc(100% + 7px);left:50%;transform:translateX(-50%);width:250px;z-index:9;background:linear-gradient(175deg,#2E2620,#241D18);border:1px solid #55483A;border-radius:8px;padding:8px 12px;font-size:12px;font-style:italic;color:#C0AF9A;box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 10px 26px rgba(0,0,0,.6);text-align:center}
.ac .cd:after{content:"";position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#55483A}
.ac:hover .cd{visibility:visible;opacity:1}
.ac:hover{z-index:30}
.ac{display:flex;gap:11px;align-items:center;background:linear-gradient(180deg,var(--oak2),#221B16);border:1px solid;border-radius:9px;padding:8px 11px;box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 2px 3px rgba(0,0,0,.4)}
.aico{flex:none;width:54px;height:54px;display:flex;align-items:center;justify-content:center;border:1px solid;border-radius:11px;background:radial-gradient(circle at 50% 35%,#2E2620,#191411 78%);box-shadow:inset 0 2px 5px rgba(0,0,0,.5),inset 0 -1px 0 rgba(255,255,255,.05)}
.atx{min-width:0}
.ac .nm{font-family:"Cormorant Garamond",Georgia,serif;font-weight:700;font-size:16px;line-height:1.25}
.ac .rar{font-family:"Cinzel","Cormorant SC",Georgia,serif;text-transform:uppercase;letter-spacing:.1em;font-size:8.5px;margin-left:7px;opacity:.85}
.ac .fl{font-size:12.5px;color:#C0AF9A;line-height:1.4;margin-top:3px}
.ac .cd{font-size:11.5px;color:var(--mut);font-style:italic;margin-top:2px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:4px 36px;align-items:start}
.more{margin-top:12px}
.more summary{cursor:pointer;list-style:none;text-align:center;font:600 11.5px "Cinzel","Cormorant SC",Georgia,serif;letter-spacing:.14em;text-transform:uppercase;color:var(--brass);padding:8px 14px;border:1px solid rgba(201,169,98,.35);border-radius:9px;background:linear-gradient(180deg,var(--oak2),#221B16);box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 2px 3px rgba(0,0,0,.4)}
.more summary::-webkit-details-marker{display:none}
.more summary:hover{color:#E0C685;border-color:rgba(201,169,98,.6)}
.more[open] summary{opacity:.65}
.h3{font:600 10.5px "Cinzel","Cormorant SC",Georgia,serif;letter-spacing:.18em;text-transform:uppercase;color:#9A8668;margin:16px 0 9px}
.lb2{display:flex;flex-direction:column;line-height:1.15}
.lb2 b{font-size:13.5px;font-weight:600;color:var(--text)}
.lb2 i{font-style:normal;font-size:10.5px;color:#8F7E6B}
.kv{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px solid #2E2620;font-size:13.5px}
.kv span{color:var(--mut)}
.kv b{font-weight:600;text-align:right;color:#D5C9B8}
.ch{position:relative;cursor:default;border-radius:15px;padding:3px 13px;font-size:13px;background:linear-gradient(180deg,var(--oak2),#221B16);border:1px solid;box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 2px 3px rgba(0,0,0,.4)}
.ch .tip{visibility:hidden;opacity:0;transition:opacity .18s;position:absolute;bottom:135%;left:50%;transform:translateX(-50%);width:268px;z-index:9;background:linear-gradient(175deg,#2E2620,#241D18);border:1px solid #55483A;border-radius:9px;padding:11px 14px;font-size:12.5px;line-height:1.5;color:var(--text);box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 10px 30px rgba(0,0,0,.65);white-space:normal}
.ch .tip:after{content:"";position:absolute;top:100%;left:50%;transform:translateX(-50%);border:7px solid transparent;border-top-color:#55483A}
.ch:hover .tip{visibility:visible;opacity:1}
.ch .tip b{font-family:"Cormorant Garamond",Georgia,serif;font-size:15px}
.ch .tip .rar{font-family:"Cinzel","Cormorant SC",Georgia,serif;text-transform:uppercase;letter-spacing:.1em;font-size:9.5px;margin-left:7px}
.ch .tip .cond{display:block;margin-top:4px;color:var(--mut);font-size:11.5px;font-style:italic}
.wch{display:inline-block;background:linear-gradient(180deg,var(--oak2),#221B16);border:1px solid #352C24;border-radius:13px;padding:2px 11px;font-size:13px;color:#C0AF9A;margin:0 4px 6px 0}
ul{margin:0;padding-left:21px}li{margin-bottom:6px;font-size:14.5px}
ul.plus li::marker{color:#A9BC6E}
.fix{margin-bottom:13px;padding:9px 13px;border-left:3px solid var(--crimson);background:linear-gradient(90deg,rgba(139,38,53,.10),transparent 70%);border-radius:0 8px 8px 0}
.fix .w{color:#D8A091;font-size:14px}
.fix .a{color:#B9C692;font-size:14px;margin-top:2px}
.fix .ev{color:var(--mut);font-size:12px;font-style:italic}
.foot{margin-top:26px;border-top:1px solid #3A312A;padding-top:13px;display:flex;justify-content:space-between;position:relative}
.seal{position:absolute;right:2px;top:-26px;width:46px;height:46px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#A63A48,var(--crimson) 55%,#5E1822);box-shadow:inset 0 2px 4px rgba(255,255,255,.18),inset 0 -3px 6px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;font:600 14px "Cinzel","Cormorant SC",Georgia,serif;color:#E8CFB4;text-shadow:0 -1px 1px rgba(0,0,0,.5)}
</style></head><body><div class="card">

<div class="head">
<!-- avatar.png если сгенерирован; нет файла — просто без <img>, заглушки запрещены -->
<img src="avatar.png" alt="монстр из титула">
<div>
<div class="muted" style="font-family:'Cinzel',Georgia,serif;letter-spacing:.3em;font-size:10.5px">PROMPT WARRIOR</div>
<h1><span class="cap">{{первая буква}}</span>{{титул без уровня, уровень уходит в табличку справа}}</h1>
<div class="ident">{{identity.class.ru}} · {{identity.race.ru}} ({{share}}% реплик)</div>
<div class="muted" style="margin-top:6px">{{N реплик · N слов · N сессий · даты · N реплик в активный день}}</div>
</div>
<div class="lvl"><b>{{уровень римскими}}</b><span>уровень {{N}}</span></div>
</div>
<div class="dstrip">{{полоса прогресса из profile.delta — только если есть изменения}}</div>

<h2><!-- иконка секции (quill-ink) -->Хроника воина</h2>
<div class="chron"><!-- 2-4 <p> авторского текста модели (правило 6); первая буква — буквица --></div>

<h2><!-- иконка секции -->Объём реплик</h2>
<div class="grid"><!-- 4 тайла: слов в среднем / медиана / короткие / спеки --></div>

<div class="cols">
<div><h2><!-- иконка секции -->Топ императивов</h2><!-- .row-бары, латунь --></div>
<div><h2><!-- иконка секции -->Маркеры тона</h2><!-- .row-бары: негатив ember, нейтраль латунь, позитив олива --></div>
</div>

<div class="duo">
<div><h2><!-- иконка секции -->Часы активности</h2><div class="hours"><!-- 24 <i>, ночные .n --></div></div>
<div><h2><!-- иконка секции -->Дни недели</h2><div class="hours" style="gap:6px"><!-- 7 <i> из metrics.weekdays (пн..вс), сб-вс .n --></div></div>
</div>

<h2><!-- иконка секции -->Шкалы</h2>
<div class="g2"><!-- ВСЕ гейджи из profile.gauges в 2 колонки, каждый в своей <div>-ячейке:
.growl (подпись+.gauge+.needle+значение) + .gnote (подпись-бакет, ссылки кликабельны) --></div>

<h2><!-- иконка секции -->Экономика и арсенал</h2>
<div class="grid6"><!-- 6 тайлов: токены / кэш-эфф / вызовы / инструменты / проекты / PR; секцию скрыть если economy null --></div>
<div class="cols">
<div><div class="h3">Топ инструментов</div><!-- .row-бары: топ-5 из arsenal.top_tools (mcp__X__tool → короткое имя), латунь --></div>
<div><div class="h3">Стиль работы — вызовы по ролям</div><!-- .row-бары с двухстрочными подписями .lb2:
Оператор (консоль: Bash, PowerShell) · Хирург (правки кода: Edit, Write) · Археолог (чтение и поиск: Read, Grep) ·
Кукловод (MCP: внешние серверы) · Прочее (остаток до 100%). НИКОГДА не показывать роль без пояснения --></div>
</div>
<div class="cols">
<div><div class="h3">MCP-парк — внешние серверы</div><!-- .row-бары из arsenal.top_mcp_servers, ember; скрыть если пусто --></div>
<div><div class="h3">Файлы в работе — топ расширений</div><!-- .row-бары из arsenal.top_extensions (.tsx N), олива --></div>
</div>

<h2><!-- иконка секции -->Боевые повадки</h2>
<div class="grid4"><!-- 12 тайлов (3 ряда по 4 — шире, текст не в столбик): прерывания/100 · точка кипения №N (+% вскипевших) · оборотень ×K ·
скриншоты/100 · дабл-тексты/100 · вызовы субагентов · «нет»-открытия % · код-свитчинг % ·
вопрос-микс (что/как/почему %) · ошибки инструментов % · thinking-доля % · число ачивок.
Тайлы с null-метрикой (напр. оборотень без ночной выборки) — опускать --></div>
<div class="cols">
<div><div class="h3">Конюшня — ответы по моделям</div><!-- .row-бары из arsenal.models (человекочитаемые имена: claude-opus-4-8 → Опус 4.8), латунь --></div>
<div><div class="h3">Сетап</div><!-- .kv строки: вход (arsenal.entrypoints) · план-режим · версий CC · самая дорогая сессия (arsenal.top_sessions[0]) --></div>
</div>

<h2><!-- иконка секции -->Словарь воина</h2>
<div><!-- .wch чипы слово ×count; скрыть если пусто --></div>

<h2>Достижения, {{N}}</h2>
<div class="chips"><!-- .ac карточки ТОЛЬКО legendary+epic (сетка 2 кол.): медальон .aico слева (иконка из assets/achievement-icons, только path, fill=currentColor, фоны выбросить) + .atx: название цветом редкости + .rar + .fl флейвор. Условие — в .cd (ховер-тултип НАД карточкой) --></div>
<details class="more"><summary>Показать все достижения — ещё {{N}} (rare и common)</summary>
<div class="chips" style="margin-top:10px"><!-- .ac карточки rare+common --></div></details>

<h2 style="color:#A9BC6E">Сильное</h2>
<ul class="plus"><!-- до 3 пунктов по правилам выбора --></ul>

<h2 style="color:#D8A091">Слабое и что делать</h2>
<!-- до 4 .fix-плашек: слабость / → что делать / пруф-ссылка -->

<div class="foot muted"><span style="font-family:'Cinzel',Georgia,serif;letter-spacing:.15em;font-size:11px">SCALE {{version}}</span><span class="seal"><!-- rune-sword 22px, #E8CFB4 --></span><span style="text-align:right">{{Понравилось? Поставьте звезду ★ / Enjoyed it? Star the repo ★}}<br><a href="https://github.com/timoncool/prompt-warrior">github.com/timoncool/prompt-warrior</a></span></div>
</div></body></html>
```

## Инлайн-виджет (если в среде есть)

Зеркалит сгенерированную карточку 1:1 — те же секции, те же числа, тот же выбор
сильного/слабого; оформление — токенами хост-системы. Ничего не изобретать.
Обязательно: кнопка «Открыть HTML-карточку». Хосты обычно НЕ открывают file://-ссылки
из виджета, поэтому кнопка должна вызывать sendPrompt('Открой <абсолютный путь>/ai-profile.html
в браузере') — модель откроет файл системной командой. Прямую file://-ссылку не использовать.
Обязательно: кнопка/ссылка «Открыть HTML-карточку» на сгенерированный файл
(`file:///<абсолютный путь>/ai-profile.html`) — рядом со ссылкой на GitHub в футере.

## Text fallback (консоль, когда нет ни браузера, ни превью, ни виджета)

Та же карточка текстом, те же правила (каждое число один раз, подписи-бакеты из profile.json):

```
PROMPT WARRIOR · SCALE v1.2
Неистовый Командир Терминала 89 уровня, «Железная Длань»
5 284 реплики · 202 485 слов · 150 сессий · 2026-05-16..2026-07-04

— Объём: 38.3 слов в среднем · медиана 11 · короткие 56.1% · спеки 3.1%

— Топ императивов          — Маркеры тона
сделай   ██████████ 556    мат          ██████████ 43.2%
проверь  ██████▏    347    вопросы      ████████▏  35.2%
...                        ...

— Шкалы
Ярость      ████████▎ 83  <подпись бакета>
Теплота     █▊        18  <подпись бакета>
...

— Достижения (14): [LEG] Тиран · [EPIC] Марафонец · [RARE] Романист · ...
   (при вопросе юзера про ачивку — дать её desc и условие из profile.json)

— Сильное: 3 пункта      — Слабое → что делать: до 4 пар (пруф — URL текстом)
```

Бары: `█` из value/max×10 блоков (частичные ▏▎▍▌▋▊▉ по остатку). Ссылки — голым URL.
Редкость ачивок — префиксом [LEG]/[EPIC]/[RARE]/[COM].
