# Card template — модель собирает карточку ПО ЭТОМУ ШАБЛОНУ

Одна карточка, один продукт: серьёзный аналитический портрет с геймифицированной
приправой — НЕ лист персонажа. Заполняй шаблон данными из profile.json, ничего не
выдумывая: структура, CSS и порядок секций — как ниже, слово в слово. Меняются только
данные и выбранные правилами пункты. Язык — язык общения юзера (в profile.json — ru/en).

## Жёсткие правила (нарушение = брак)

1. **Каждое число появляется на карточке ровно один раз.** Поздние секции ссылаются
   на ранние словами («медиана — в Объёме», «см. маркеры»), не перепечатывают.
2. Замечание про исследования тона — один раз, в подписи шкалы «Ярость». Больше нигде.
2в. Шкалы (gauges) — все четыре из profile.json, с готовыми подписями-бакетами; не выдумывать свои формулы и тексты.
2а. Все упоминания источников (arxiv, Anthropic docs) — КЛИКАБЕЛЬНЫЕ <a href>, не голый текст.
2б. Каждый чип ачивки несёт стилизованный CSS-тултип (.tip): название + редкость + флейвор (desc_*) + условие (cond_*) из profile.json. Браузерный атрибут title не использовать.
3. Никаких картинок: ни аватаров, ни иконок, ни SVG, ни base64, ни внешних ресурсов.
4. Отдельной секции «Рекомендации» НЕТ — советы живут парами в «Слабое → что делать».
5. Числа — из profile.json как есть, без округлений и смягчений.

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

## HTML-шаблон (заполнить плейсхолдеры {{...}}, списки — по образцу строки)

```html
<!doctype html><html lang="{{lang}}"><head><meta charset="utf-8"><title>Prompt Warrior</title><style>
:root{--bg:#0d0b12;--card:#151021;--panel:#1e1731;--line:#2c2440;--text:#ece8f4;--mut:#928aa8;--acc:#8b5cf6;--gold:#f59e0b}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font:15px/1.6 "Segoe UI",system-ui,sans-serif;display:flex;justify-content:center;padding:28px;margin:0}
.card{width:780px;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:34px 38px}
h1{font:600 24px/1.3 Georgia,serif;margin:2px 0 4px;letter-spacing:.2px}
h2{font-size:12px;margin:26px 0 10px;color:var(--mut);text-transform:uppercase;letter-spacing:.14em;display:flex;align-items:center;gap:10px}
h2:after{content:"";flex:1;height:1px;background:var(--line)}
.muted{color:var(--mut);font-size:13px}
a{color:#9f8fef;text-decoration:none;border-bottom:1px dotted #5b4d85}
a:hover{color:#c4b5fd}
.alt{color:var(--gold);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.tile{background:var(--panel);border-radius:12px;padding:11px 14px}
.tile b{font-size:20px;display:block;font-variant-numeric:tabular-nums}
.tile span{font-size:12px;color:var(--mut)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:8px 30px}
.row{display:flex;align-items:center;gap:9px;margin-bottom:6px}
.row .lb{width:128px;font-size:12.5px;color:var(--mut);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{flex:1;height:10px;background:var(--panel);border-radius:5px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:5px}
.row .vl{width:48px;font-size:12.5px;font-variant-numeric:tabular-nums}
.duo{display:grid;grid-template-columns:1.35fr 1fr;gap:30px;align-items:end}
.hours{display:flex;align-items:flex-end;gap:2px;height:52px}
.hours i{flex:1;background:#4d4468;border-radius:2px 2px 0 0}
.hours i.n{background:var(--acc)}
.rage{height:8px;border-radius:4px;background:linear-gradient(90deg,#22c55e,#eab308,#ef4444);position:relative;margin-top:8px}
.rage s{position:absolute;top:-4px;width:3px;height:16px;background:#fff;border-radius:2px;text-decoration:none}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.ch{border:1px solid;border-radius:14px;padding:2.5px 12px;font-size:12.5px;position:relative;cursor:default}
.ch .tip{visibility:hidden;opacity:0;transition:opacity .15s;position:absolute;bottom:130%;left:50%;transform:translateX(-50%);width:256px;background:#221a38;border:1px solid #3a2f58;border-radius:10px;padding:10px 13px;font-size:12px;line-height:1.55;color:var(--text);z-index:9;box-shadow:0 8px 28px rgba(0,0,0,.55);white-space:normal}
.ch .tip:after{content:"";position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#3a2f58}
.ch:hover .tip{visibility:visible;opacity:1}
.ch .tip b{font-size:12.5px}
.ch .tip .rar{text-transform:uppercase;letter-spacing:.08em;font-size:10px;margin-left:6px}
.ch .tip .cond{display:block;margin-top:4px;color:var(--mut);font-size:11px}
ul{margin:0;padding-left:20px}li{margin-bottom:6px;font-size:14px}
ul.plus li::marker{color:#22c55e}
.fix{margin-bottom:13px;padding-left:12px;border-left:2px solid #7f1d1d}
.fix .w{color:#f0a8a8;font-size:14px}
.fix .a{color:#a7e3a7;font-size:14px;margin-top:2px}
.fix .ev{color:var(--mut);font-size:12px;margin-top:1px}
.foot{margin-top:26px;border-top:1px solid var(--line);padding-top:12px;display:flex;justify-content:space-between}
</style></head><body><div class="card">

<div class="muted">Prompt Warrior</div>
<h1>{{title в языке юзера}}</h1>
<div class="muted" style="margin-top:6px">{{N реплик · N слов · N сессий · даты · N реплик/активный день}}</div>
<!-- если low_confidence: жёлтая плашка «Мало данных (<100 реплик) — профиль ориентировочный» -->

<h2>Объём реплик</h2>
<div class="grid">
<div class="tile"><b>{{words_per_message}}</b><span>слов в среднем</span></div>
<div class="tile"><b>{{median_words_voice}}</b><span>слов — медиана</span></div>
<div class="tile"><b>{{quick_share_pct}}%</b><span>короткие (≤12 слов)</span></div>
<div class="tile"><b>{{long_share_pct}}%</b><span>спеки (200+ слов)</span></div>
</div>

<div class="cols">
<div><h2>Топ императивов</h2>
<!-- по строке на каждый из metrics.top_imperatives; ширина = count/max*100%; цвет всех баров var(--acc) -->
<div class="row"><span class="lb">{{label}}</span><span class="bar"><i style="width:{{pct}}%;background:var(--acc)"></i></span><span class="vl">{{count}}</span></div>
</div>
<div><h2>Маркеры тона, % реплик</h2>
<!-- строки по убыванию: мат, вопросы, капс, оскорбления, !!!!/????, verify, самокоррекция, вежливость.
     негативные маркеры #ef4444, вопросы var(--acc), позитивные #22c55e; ширина = value/max*100% -->
<div class="row"><span class="lb">{{маркер}}</span><span class="bar"><i style="width:{{pct}}%;background:{{цвет}}"></i></span><span class="vl">{{value}}%</span></div>
</div>
</div>

<div class="duo">
<div><h2>Активность по часам (местное время)</h2>
<div class="hours"><!-- 24 <i>: height = value/max*52px (мин 4); часы 00-05 и 23 — class="n"; title="HH:00 — N" --></div>
<div style="display:flex;justify-content:space-between" class="muted"><span>00</span><span>06</span><span>12</span><span>18</span><span>23</span></div></div>
<div><h2>Шкалы</h2>
<!-- по одной строке на каждый gauge из profile.gauges (4 шт): имя, полоска с маркером, значение, подпись из caption_ru/en.
     Подписи берутся ГОТОВЫМИ из profile.json (бакеты уже выбраны анализатором); в подписи ярости ссылки arxiv — кликабельные -->
<div class="gaugerow"><span class="glabel">{{ru}}</span><div class="rage"><s style="left:{{value}}%"></s></div><span class="gval">{{value}}</span></div>
<div class="muted" style="font-size:11px;margin-top:5px">{{подпись по бакету — ссылки ВСЕГДА кликабельные <a href>:
  rage ≥ 60 → «на качество ответов почти не влияет (агрегатный эффект тона ≈ 0 — <a href="https://arxiv.org/abs/2508.00614">arxiv 2508.00614</a>, <a href="https://arxiv.org/html/2512.12812v1">2512.12812</a>) — но жрёт токены без диагностики»
  20–59   → «умеренный градус; тон почти не влияет на качество ответов (<a href="https://arxiv.org/abs/2508.00614">arxiv 2508.00614</a>)»
  < 20    → «дзен-режим: усилители (капс, мат, !!!) почти не используются»}}</div></div>
</div>

<h2>Достижения — {{N}}</h2>
<div class="chips">
<!-- чип на каждую ачивку, цвет рамки/текста по редкости:
     legendary #f59e0b/#fbbf24 · epic #a855f7/#c084fc · rare #3b82f6/#93c5fd · common #9aa0a6/#b6bbc2 -->
<span class="ch" style="border-color:{{c1}};color:{{c2}}">{{название}}<span class="tip"><b>{{название}}</b><span class="rar" style="color:{{c2}}">{{rarity}}</span><br>{{desc — флейвор из profile.json (desc_ru/desc_en)}}<span class="cond">условие: {{cond_ru/cond_en}}</span></span></span>
<!-- тултип ОБЯЗАТЕЛЕН на каждом чипе: стилизованный .tip (не браузерный title) с названием,
     редкостью, флейвор-описанием и условием из profile.json -->
</div>

<h2>Экономика и арсенал</h2>
<!-- опционально, если profile.economy/arsenal есть: одна строка тайлов —
     токенов сгенерировано (в M), кэш-эффективность %, вызовов инструментов, топ-3 инструмента
     текстом, моделей в ходу, проектов. Числа один раз, без второй ярусной детализации -->
<div class="grid">{{тайлы экономики/арсенала}}</div>

<h2>Словарь воина</h2>
<!-- опционально: если metrics.signature_words непуст — одна строка приглушённых чипов
     «слово ×count»; это фирменная лексика юзера, подавать с юмором, без оценок -->
<div class="chips">{{чипы слов}}</div>

<h2 style="color:#86c98a">Сильное</h2>
<ul class="plus"><!-- до 3 пунктов по правилам выбора выше --><li>{{пункт}}</li></ul>

<h2 style="color:#e08b8b">Слабое → что делать</h2>
<!-- до 4 пар по правилам выбора выше -->
<div class="fix"><div class="w">{{слабость}}</div><div class="a">→ {{что делать}}</div><div class="ev">{{пруф — с кликабельной ссылкой: Anthropic docs → <a href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices">…</a>, context rot → <a href="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents">…</a>, arxiv → прямые ссылки; «практика» — без ссылки}}</div></div>

<div class="foot muted"><span>SCALE v1 · prompt-warrior</span><span>github.com/timoncool/prompt-warrior</span></div>
</div></body></html>
```

## Инлайн-виджет (если в среде есть)

Зеркалит сгенерированную карточку 1:1 — те же секции, те же числа, тот же выбор
сильного/слабого; оформление — токенами хост-системы. Ничего не изобретать.

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
