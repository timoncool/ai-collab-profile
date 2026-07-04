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
4а. Идентичность: строка под титулом «{класс} · {раса} ({доля}% реплик)» из profile.identity;
   расу опускать если identity.race == null; класс есть всегда.
4б. Аватар: если рядом с карточкой есть avatar.png (scripts/avatar.py, robohash) —
   <img src="avatar.png"> слева в шапке, 120-140px, скруглённый. Файла нет — шапка без
   картинки; заглушки, буквы и иконки вместо аватара ЗАПРЕЩЕНЫ.
4в. Иконки ачивок: assets/achievement-icons/<id>.svg, при отсутствии — _<rarity>.svg
   (game-icons.net CC-BY-3.0, атрибуция в ATTRIBUTION.md). В чип — инлайн 13-14px перед
   названием: только <path> из файла с fill="currentColor", фоновые прямоугольники
   выбрасывать — иконка красится цветом редкости.
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

## HTML-шаблон «Гримуар v1» (утверждён юзером: без арки, без римских цифр; заполнить {{...}})

Шрифты Google (Cormorant Garamond / Cinzel / Crimson Pro) подключать <link>-ом как в
образце; офлайн деградирует на Georgia — допустимо.

```html
<!doctype html><html lang="{{lang}}"><head><meta charset="utf-8"><title>Prompt Warrior</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Cinzel:wght@500;600&family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{--bg:#120e0b;--card:#1C1714;--oak:#251E19;--oak2:#2B231D;--line:#4A3F35;--text:#E8DFD4;--mut:#9C8B7A;--brass:#C9A962;--brass-dim:#8F7440;--crimson:#8B2635}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font:15.5px/1.6 "Crimson Pro",Georgia,serif;display:flex;justify-content:center;padding:28px;margin:0}
.card{width:820px;background:linear-gradient(170deg,#201A15 0%,var(--card) 22%,#191411 100%);border:1px solid #3A312A;border-radius:14px;padding:34px 40px;position:relative;
box-shadow:0 1px 0 rgba(255,255,255,.05) inset,0 -2px 0 rgba(0,0,0,.35) inset,0 2px 6px rgba(0,0,0,.5),0 18px 50px rgba(0,0,0,.55)}
.card:before{content:"";position:absolute;inset:0;border-radius:14px;pointer-events:none;z-index:2;
background:radial-gradient(120% 90% at 50% 8%,transparent 50%,rgba(0,0,0,.34) 100%),url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"/></filter><rect width="140" height="140" filter="url(%23n)" opacity="0.045"/></svg>')}
.card>*{position:relative;z-index:3}
.card:after{content:"";position:absolute;inset:10px;border:1px solid rgba(201,169,98,.22);border-radius:9px;pointer-events:none}
h1{font:600 30px/1.22 "Cormorant Garamond",Georgia,serif;margin:8px 0 3px;text-shadow:0 1px 0 rgba(0,0,0,.6)}
h2{font:600 12.5px "Cinzel",Georgia,serif;letter-spacing:.2em;text-transform:uppercase;color:var(--brass);margin:26px 0 12px;display:flex;align-items:center;gap:11px}
h2:before{content:"";width:24px;height:1px;background:linear-gradient(90deg,transparent,var(--brass-dim))}
h2:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--brass-dim),transparent 85%)}
.muted{color:var(--mut);font-size:13px}
a{color:var(--brass);text-decoration:none;border-bottom:1px dotted var(--brass-dim)}a:hover{color:#E0C685}
.head{display:flex;gap:20px;align-items:center;padding-bottom:16px;border-bottom:1px solid rgba(201,169,98,.25);position:relative}
.head img{width:112px;height:112px;border-radius:12px;border:2px solid rgba(201,169,98,.4);background:#171310;box-shadow:0 3px 10px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.1);flex:none}
.ident{font:600 13px "Cinzel",Georgia,serif;letter-spacing:.08em;color:var(--brass)}
.lvl{flex:none;text-align:center;padding:11px 13px;border:1px solid rgba(201,169,98,.4);border-radius:10px;background:linear-gradient(180deg,#2B231D,#1E1813);box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 3px 8px rgba(0,0,0,.45)}
.lvl b{display:block;font:600 22px "Cinzel",Georgia,serif;color:var(--brass);letter-spacing:.04em}
.lvl span{display:block;font-size:10px;color:var(--mut);letter-spacing:.14em;text-transform:uppercase;margin-top:2px}
.dstrip{margin-top:12px;padding:6px 13px;border:1px solid #3A312A;border-radius:8px;font-size:13px;color:var(--mut);background:rgba(37,30,25,.7)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
.grid6{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
.tile{background:linear-gradient(180deg,var(--oak2),var(--oak));border-radius:9px;padding:11px 13px;border:1px solid #352C24;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),inset 0 -2px 4px rgba(0,0,0,.35),0 1px 2px rgba(0,0,0,.4)}
.tile b{font-size:21px;display:block;font-variant-numeric:tabular-nums;font-family:"Cormorant Garamond",Georgia,serif;font-weight:700}
.tile span{font-size:11.5px;color:var(--mut)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:8px 32px}
.row{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.row .lb{width:130px;font-size:13px;color:var(--mut);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{flex:1;height:12px;background:#171310;border-radius:6px;overflow:hidden;border:1px solid #322A23;box-shadow:inset 0 2px 4px rgba(0,0,0,.55)}
.bar i{display:block;height:100%;border-radius:5px;box-shadow:inset 0 1px 0 rgba(255,255,255,.25)}
.row .vl{width:50px;font-size:13px;font-variant-numeric:tabular-nums}
.duo{display:grid;grid-template-columns:1.15fr 1fr;gap:32px;align-items:start}
.hours{display:flex;align-items:flex-end;gap:3px;height:52px;padding:6px 8px 0;background:#171310;border:1px solid #322A23;border-radius:8px;box-shadow:inset 0 2px 5px rgba(0,0,0,.5)}
.hours i{flex:1;background:linear-gradient(180deg,#5C4F41,#463B30);border-radius:2px 2px 0 0;box-shadow:inset 0 1px 0 rgba(255,255,255,.12)}
.hours i.n{background:linear-gradient(180deg,#D8B872,#A5843F);box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 0 6px rgba(201,169,98,.25)}
.growl{display:flex;align-items:center;gap:10px;margin-bottom:3px}
.glb{width:88px;font-size:13px;color:var(--mut);text-align:right}
.gvl{width:28px;font-size:13px;font-variant-numeric:tabular-nums}
.gauge{height:12px;border-radius:6px;border:1px solid #322A23;background:linear-gradient(90deg,#6E7F46,#A08430 45%,#9C4A26 75%,#7E2B20);box-shadow:inset 0 2px 4px rgba(0,0,0,.45);position:relative}
.needle{position:absolute;top:-4px;width:4px;height:20px;background:linear-gradient(180deg,#F0DCAC,#C9A962 60%,#8F7440);border-radius:2px;box-shadow:0 0 4px rgba(0,0,0,.6),0 0 8px rgba(201,169,98,.4)}
.gnote{font-size:11px;margin:0 30px 9px 98px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.ch{position:relative;cursor:default;border-radius:15px;padding:3px 13px;font-size:13px;background:linear-gradient(180deg,var(--oak2),#221B16);border:1px solid;box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 2px 3px rgba(0,0,0,.4)}
.ch .tip{visibility:hidden;opacity:0;transition:opacity .18s;position:absolute;bottom:135%;left:50%;transform:translateX(-50%);width:268px;z-index:9;background:linear-gradient(175deg,#2E2620,#241D18);border:1px solid #55483A;border-radius:9px;padding:11px 14px;font-size:12.5px;line-height:1.5;color:var(--text);box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 10px 30px rgba(0,0,0,.65);white-space:normal}
.ch .tip:after{content:"";position:absolute;top:100%;left:50%;transform:translateX(-50%);border:7px solid transparent;border-top-color:#55483A}
.ch:hover .tip{visibility:visible;opacity:1}
.ch .tip b{font-family:"Cormorant Garamond",Georgia,serif;font-size:15px}
.ch .tip .rar{font-family:"Cinzel",Georgia,serif;text-transform:uppercase;letter-spacing:.1em;font-size:9.5px;margin-left:7px}
.ch .tip .cond{display:block;margin-top:4px;color:var(--mut);font-size:11.5px;font-style:italic}
.wch{display:inline-block;background:linear-gradient(180deg,var(--oak2),#221B16);border:1px solid #352C24;border-radius:13px;padding:2px 11px;font-size:12.5px;color:var(--mut);margin:0 4px 6px 0}
ul{margin:0;padding-left:21px}li{margin-bottom:6px;font-size:14.5px}
ul.plus li::marker{color:#A9BC6E}
.fix{margin-bottom:13px;padding:9px 13px;border-left:3px solid var(--crimson);background:linear-gradient(90deg,rgba(139,38,53,.10),transparent 70%);border-radius:0 8px 8px 0}
.fix .w{color:#D8A091;font-size:14px}
.fix .a{color:#B9C692;font-size:14px;margin-top:2px}
.fix .ev{color:var(--mut);font-size:12px;font-style:italic}
.foot{margin-top:26px;border-top:1px solid #3A312A;padding-top:13px;display:flex;justify-content:space-between;position:relative}
.seal{position:absolute;right:2px;top:-24px;width:42px;height:42px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#A63A48,var(--crimson) 55%,#5E1822);box-shadow:inset 0 2px 4px rgba(255,255,255,.18),inset 0 -3px 6px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;font:600 14px "Cinzel",Georgia,serif;color:#E8CFB4;text-shadow:0 -1px 1px rgba(0,0,0,.5)}
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

<h2>Объём реплик</h2>
<div class="grid"><!-- 4 тайла: слов в среднем / медиана / короткие / спеки --></div>

<div class="cols">
<div><h2>Топ императивов</h2><!-- .row-бары, латунь --></div>
<div><h2>Маркеры тона</h2><!-- .row-бары: негатив ember, нейтраль латунь, позитив олива --></div>
</div>

<div class="duo">
<div><h2>Часы активности</h2><div class="hours"><!-- 24 <i>, ночные .n --></div></div>
<div><h2>Шкалы</h2><!-- 4 гейджа .growl+.gauge+.needle, подписи-бакеты из profile.gauges, ссылки кликабельны --></div>
</div>

<h2>Экономика и арсенал</h2>
<div class="grid6"><!-- 6 тайлов: токены / кэш-эфф / вызовы / инструменты / проекты / PR; секцию скрыть если economy null --></div>
<div class="muted"><!-- строка: топ-3 инструмента · доли категорий · MCP% --></div>

<h2>Словарь воина</h2>
<div><!-- .wch чипы слово ×count; скрыть если пусто --></div>

<h2>Достижения, {{N}}</h2>
<div class="chips"><!-- .ch чипы: инлайн-иконка (assets/achievement-icons, только path, fill=currentColor, фон-прямоугольники выбросить) + название + .tip тултип --></div>

<h2 style="color:#A9BC6E">Сильное</h2>
<ul class="plus"><!-- до 3 пунктов по правилам выбора --></ul>

<h2 style="color:#D8A091">Слабое и что делать</h2>
<!-- до 4 .fix-плашек: слабость / → что делать / пруф-ссылка -->

<div class="foot muted"><span style="font-family:'Cinzel',Georgia,serif;letter-spacing:.15em;font-size:11px">SCALE {{version}}</span><span class="seal">PW</span><span><a href="https://github.com/timoncool/prompt-warrior">github.com/timoncool/prompt-warrior</a></span></div>
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
