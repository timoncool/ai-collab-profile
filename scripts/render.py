#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Warrior — canonical card renderer.

The MODEL never writes HTML/CSS/SVG. It authors its part in content.json and runs:

  python scripts/render.py profile.json --content content.json --lang ru -o ai-profile.html

content.json (everything the model writes, in the card language):
{
  "chronicle": ["<p> text...", "..."],          // 2-4 paragraphs, may contain <em>, NO numbers
  "strengths": ["...", "..."],                  // 1-3, picked by widget.md rules
  "weaknesses": [                               // up to 4, picked by widget.md rules
    {"w": "weakness", "a": "what to do", "ev": "evidence note", "url": "https://..." }
  ],
  "delta_note": "optional custom delta strip"   // omit/null -> built from profile.delta
}

Everything numeric/mechanical (tiles, bars, gauges, icons, favicon, seal, accordion)
comes from profile.json + assets automatically. CSS is taken from the template block in
references/widget.md — single source of truth.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icons  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRASS = "linear-gradient(180deg,#D8B872,#A5843F)"
EMBER = "linear-gradient(180deg,#D4744A,#9C4A26)"
OLIVE = "linear-gradient(180deg,#A9BC6E,#77893F)"
GRAY = "linear-gradient(180deg,#5C4F41,#463B30)"
RC = {"legendary": ("#C9A962", "#E4C77E"), "epic": ("#8E6FB0", "#B79CD4"),
      "rare": ("#5E7F9B", "#8FB0C9"), "common": ("#6E6459", "#9C9184")}

L = {
    "ru": {
        "lang": "ru", "level": "уровень", "chronicle": "Хроника воина",
        "volume": "Объём реплик", "imperatives": "Топ императивов", "tone": "Маркеры тона",
        "hours": "Часы активности", "days": "Дни недели", "gauges": "Шкалы",
        "economy": "Экономика и арсенал", "habits": "Боевые повадки",
        "words": "Словарь воина", "achievements": "Достижения",
        "strong": "Сильное", "weak": "Слабое и что делать",
        "wd": ["пн", "вт", "ср", "чт", "пт", "сб", "вс"],
        "corpus": "%s реплик · %s слов · %d сессий · %s..%s · %s реплик в активный день",
        "v_avg": "слов в среднем", "v_med": "слов, медиана",
        "v_short": "короткие (до 12 слов)", "v_spec": "спеки (от 200 слов)",
        "tone_rows": ["мат", "вопросы", "капс, крик", "оскорбления", "!!!! и ????",
                      "проверь-запросы", "самокоррекция", "вежливость"],
        "e_tok": "токенов сгенерировано", "e_cache": "кэш-эффективность",
        "e_calls": "вызовов инструментов", "e_tools": "разных инструментов",
        "e_proj": "проектов (%s %s%%)", "e_pr": "PR и MR из сессий",
        "h_tools": "Топ инструментов", "h_roles": "Стиль работы — вызовы по ролям",
        "h_mcp": "MCP-парк — внешние серверы", "h_ext": "Файлы в работе — топ расширений",
        "h_models": "Конюшня — ответы по моделям", "h_setup": "Сетап",
        "roles": [("Оператор", "консоль: Bash, PowerShell"), ("Хирург", "правки кода: Edit, Write"),
                  ("Археолог", "чтение и поиск: Read, Grep"), ("Кукловод", "MCP: внешние серверы"),
                  ("Прочее", "всё остальное")],
        "hab": ["прерываний на 100 реплик",
                "точка кипения: реплика первой вспышки (кипит %s%% сессий)",
                "оборотень: ночной мат к дневному",
                "скриншотов на 100 реплик",
                "дабл-текстов на 100 реплик — мысли очередями",
                "вызовов субагентов — армии по одному слову",
                "реплик открываются с «нет / не так»",
                "реплик мешают RU и EN в одной фразе",
                "вопросов — «что», %s%% «как», %s%% «почему»",
                "вызовов инструментов — с ошибкой",
                "ответов модели — с thinking-блоками",
                "достижений открыто"],
        "setup": ["вход в Claude Code", "план-режим", "версий Claude Code за период",
                  "самая дорогая сессия"],
        "activations": "%d включений", "tokens_of": "«%s» — %s токенов",
        "ep": {"claude-desktop": "desktop-приложение", "cli": "терминал", "vscode": "VS Code"},
        "models": {"claude-opus-4-8": "Опус 4.8", "claude-opus-4-7": "Опус 4.7",
                   "claude-opus-4-6": "Опус 4.6", "claude-fable-5": "Фейбл 5",
                   "claude-sonnet-5": "Сонет 5", "claude-haiku-4-5": "Хайку 4.5"},
        "more": "Показать все достижения — ещё %d (rare и common)",
        "cond": "условие: %s", "ident": "%s · %s (%s%% реплик)",
        "first_run": "Первое знакомство: профиль записан в локальную историю — "
                     "возвращайтесь через неделю за новыми ачивками, левел-апами и сдвигами метрик",
        "delta_new": "новые достижения: %s", "delta_lvl": "уровень %s → %s",
        "delta_msgs": "+%d реплик", "delta_none": "с прошлого прогона (%s) без изменений",
        "delta_since": "С прошлого прогона (%s): ",
        "star": "Понравилось? Поставьте звезду ★",
        "balanced": "Ровный сбалансированный стиль — без выраженных перекосов",
        "alt_avatar": "монстр из титула",
        "title_re": r"^(.*?) (\d+) уровня(?:, (.*))?$", "q": ("«", "»"),
    },
    "en": {
        "lang": "en", "level": "level", "chronicle": "Warrior’s Chronicle",
        "volume": "Message volume", "imperatives": "Top imperatives", "tone": "Tone markers",
        "hours": "Hours of activity", "days": "Days of week", "gauges": "Gauges",
        "economy": "Economy &amp; arsenal", "habits": "Battle habits",
        "words": "Warrior’s vocabulary", "achievements": "Achievements",
        "strong": "Strong", "weak": "Weak — and what to do",
        "wd": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        "corpus": "%s messages · %s words · %d sessions · %s..%s · %s messages per active day",
        "v_avg": "words on average", "v_med": "words, median",
        "v_short": "short (up to 12 words)", "v_spec": "specs (200+ words)",
        "tone_rows": ["profanity", "questions", "CAPS, shouting", "insults", "!!!! and ????",
                      "verify-requests", "self-correction", "politeness"],
        "e_tok": "tokens generated", "e_cache": "cache efficiency",
        "e_calls": "tool calls", "e_tools": "distinct tools",
        "e_proj": "projects (%s %s%%)", "e_pr": "PRs and MRs shipped",
        "h_tools": "Top tools", "h_roles": "Working style — calls by role",
        "h_mcp": "MCP fleet — external servers", "h_ext": "Files touched — top extensions",
        "h_models": "The stable — replies by model", "h_setup": "Setup",
        "roles": [("Operator", "console: Bash, PowerShell"), ("Surgeon", "code edits: Edit, Write"),
                  ("Archaeologist", "reading & search: Read, Grep"), ("Puppeteer", "MCP: external servers"),
                  ("Other", "everything else")],
        "hab": ["interruptions per 100 messages",
                "boiling point: first-flare message (%s%% of sessions boil)",
                "werewolf: night profanity vs day",
                "screenshots per 100 messages",
                "double-texts per 100 — thoughts in salvos",
                "subagent spawns — armies at a word",
                "messages open with “no / wrong”",
                "messages mix RU and EN in one phrase",
                "of questions ask “what”, %s%% “how”, %s%% “why”",
                "of tool calls error out",
                "of replies carry thinking blocks",
                "achievements unlocked"],
        "setup": ["Claude Code entrypoint", "plan mode", "Claude Code versions in period",
                  "most expensive session"],
        "activations": "%d activations", "tokens_of": "“%s” — %s tokens",
        "ep": {"claude-desktop": "desktop app", "cli": "terminal", "vscode": "VS Code"},
        "models": {"claude-opus-4-8": "Opus 4.8", "claude-opus-4-7": "Opus 4.7",
                   "claude-opus-4-6": "Opus 4.6", "claude-fable-5": "Fable 5",
                   "claude-sonnet-5": "Sonnet 5", "claude-haiku-4-5": "Haiku 4.5"},
        "more": "Show all achievements — %d more (rare & common)",
        "cond": "unlock: %s", "ident": "%s · %s (%s%% of replies)",
        "first_run": "First acquaintance: the profile is saved to local history — "
                     "come back in a week for new achievements, level-ups and metric shifts",
        "delta_new": "new achievements: %s", "delta_lvl": "level %s → %s",
        "delta_msgs": "+%d messages", "delta_none": "no changes since the last run (%s)",
        "delta_since": "Since the last run (%s): ",
        "star": "Enjoyed it? Star the repo ★",
        "balanced": "An even, balanced style — no pronounced extremes",
        "alt_avatar": "monster from the title",
        "title_re": r"^(.*?), level (\d+)(?:, (.*))?$", "q": ("“", "”"),
    },
}

SECT_ICONS = {"chronicle": "quill-ink", "volume": "scroll-unfurled", "imperatives": "crossed-swords",
              "tone": "flame", "hours": "sands-of-time", "days": "sands-of-time", "gauges": "scales",
              "economy": "two-coins", "habits": "paw-print", "words": "spell-book",
              "achievements": "laurels", "strong": "muscle-up", "weak": "broken-bone"}


def fmt(n):
    return "{:,}".format(n).replace(",", " ")


def fm(n):
    return "%.1fM" % (n / 1e6) if n >= 1e6 else fmt(n)


def css_from_template():
    wm = open(os.path.join(ROOT, "references", "widget.md"), encoding="utf-8").read()
    block = wm[wm.index("```html"):]
    return block[block.index("<style>") + 7:block.index("</style>")]


def h2(l, key, extra=""):
    return '<h2%s>%s%s</h2>' % (extra, icons.section(SECT_ICONS[key]), l[key])


def bar_row(label, value, vmax, grad, val_text, sub=None):
    lb = ('<span class="lb lb2"><b>%s</b><i>%s</i></span>' % (label, sub)) if sub else \
         ('<span class="lb">%s</span>' % label)
    return ('<div class="row">%s<span class="bar"><i style="width:%d%%;background:%s"></i></span>'
            '<span class="vl">%s</span></div>' % (lb, max(2, round(100.0 * value / vmax)), grad, val_text))


def gauge_link(caption):
    return caption.replace("arxiv 2508.00614", '<a href="https://arxiv.org/abs/2508.00614">arxiv 2508.00614</a>') \
                  .replace("2512.12812", '<a href="https://arxiv.org/html/2512.12812v1">2512.12812</a>')


def ach_card(x, l):
    border, clr = RC[x["rarity"]]
    return ('<div class="ac" style="border-color:%s55">'
            '<div class="aico" style="color:%s;border-color:%s40">%s</div>'
            '<div class="atx"><div class="nm" style="color:%s">%s'
            '<span class="rar" style="color:%s">%s</span></div><div class="fl">%s</div>'
            '</div><div class="cd">%s</div></div>'
            % (border, clr, border, icons.achievement(x["id"], x["rarity"], 38),
               clr, x[l["lang"]], border, x["rarity"], x["desc_" + l["lang"]],
               l["cond"] % x["cond_" + l["lang"]]))


def delta_strip(p, l, custom):
    if custom:
        return custom
    d = p.get("delta")
    if not d:
        return l["first_run"]
    parts = []
    if d.get("new_achievements"):
        names = ", ".join("«%s»" % a[l["lang"]] if l["lang"] == "ru" else a[l["lang"]]
                          for a in d["new_achievements"][:3])
        extra = len(d["new_achievements"]) - 3
        parts.append(l["delta_new"] % (names + (" +%d" % extra if extra > 0 else "")))
    if d["level"]["from"] != d["level"]["to"]:
        parts.append(l["delta_lvl"] % (d["level"]["from"], d["level"]["to"]))
    if d.get("messages_added"):
        parts.append(l["delta_msgs"] % d["messages_added"])
    if not parts:
        return l["delta_none"] % d.get("since", "?")
    return l["delta_since"] % d.get("since", "?") + " · ".join(parts)


def render(p, content, lang, avatar):
    l = L[lang]
    m, e, a, ident = p["metrics"], p["economy"], p["arsenal"], p["identity"]

    mt = re.match(l["title_re"], p["title"][lang])
    h1 = mt.group(1) + ("" if not mt.group(3) else ", %s%s%s" % (l["q"][0], mt.group(3), l["q"][1]))

    imps = [(x[lang], x["count"]) for x in m["top_imperatives"]]
    imp_rows = "\n".join(bar_row(n, c, imps[0][1], BRASS, str(c)) for n, c in imps)

    tvals = [m["profanity_msg_pct"], m["question_pct"], m["caps_pct"], m["insult_pct"],
             m["multipunct_pct"], m["verify_pct"], m["self_correction_pct"], m["politeness_pct"]]
    tgrads = [EMBER, BRASS, EMBER, EMBER, EMBER, OLIVE, OLIVE, OLIVE]
    tmx = max(tvals)
    tone_rows = "\n".join(bar_row(l["tone_rows"][i], tvals[i], tmx, tgrads[i], "%s%%" % tvals[i])
                          for i in range(8))

    hrs = m["hours_local"]; hmx = max(hrs)
    hours = "".join('<i class="%s" style="height:%dpx" title="%02d:00 — %d"></i>'
                    % ("n" if (h <= 5 or h == 23) else "", max(5, round(46.0 * hrs[h] / hmx)), h, hrs[h])
                    for h in range(24))
    wd = m.get("weekdays") or [0] * 7
    wmx = max(wd) or 1
    days = "".join('<i class="%s" style="height:%dpx" title="%s — %d"></i>'
                   % ("n" if d >= 5 else "", max(5, round(46.0 * wd[d] / wmx)), l["wd"][d], wd[d])
                   for d in range(7))
    days_lb = "".join("<span>%s</span>" % x for x in l["wd"])

    gauges = "\n".join(
        '<div><div class="growl"><span class="glb">%s</span><div class="gauge" style="flex:1">'
        '<span class="needle" style="left:%d%%"></span></div><span class="gvl">%d</span></div>'
        '<div class="muted gnote">%s</div></div>'
        % (g[lang], g["value"], g["value"], gauge_link(g["caption_" + lang]))
        for g in p["gauges"])

    words = " ".join('<span class="wch">%s ×%d</span>' % (w["word"], w["count"])
                     for w in m["signature_words"])

    def short_tool(n):
        return n.split("__")[-1].replace("_", " ") if n.startswith("mcp__") else n
    tt = [(short_tool(t["name"]), t["count"]) for t in a["top_tools"][:5]]
    tools_bars = "\n".join(bar_row(n, c, tt[0][1], BRASS, fmt(c)) for n, c in tt)

    cs = a["category_shares_pct"]
    vals = [cs["operator"], cs["surgeon"], cs["archaeologist"], a["mcp_share_pct"]]
    vals.append(round(100 - sum(vals), 1))
    grads = [BRASS, OLIVE, OLIVE, EMBER, GRAY]
    cmx = max(vals)
    cats_bars = "\n".join(bar_row(l["roles"][i][0], vals[i], cmx, grads[i], "%s%%" % vals[i],
                                  sub=l["roles"][i][1]) for i in range(5))

    mcp = [(x["name"].replace("_", " "), x["count"]) for x in a["top_mcp_servers"]]
    mcp_bars = "\n".join(bar_row(n, c, mcp[0][1], EMBER, fmt(c)) for n, c in mcp) if mcp else ""
    ext = [("." + x["ext"], x["count"]) for x in a["top_extensions"]]
    ext_bars = "\n".join(bar_row(n, c, ext[0][1], OLIVE, fmt(c)) for n, c in ext) if ext else ""

    qt = m["question_types_pct"]
    hab_vals = [str(m["interruptions_per_100"]),
                ("№%s" % m["boiling_point_median"]) if m["boiling_point_median"] else None,
                ("×%s" % m["werewolf_ratio"]) if m["werewolf_ratio"] is not None else None,
                str(m["images_per_100"]), str(m["double_texts_per_100"]),
                fmt(m["subagent_spawn_calls"]), "%s%%" % m["reject_openers_pct"],
                "%s%%" % m["code_switching_pct"], "%s%%" % round(qt["what"]),
                "%s%%" % m["tool_error_pct"], "%s%%" % round(m["thinking_share_pct"]),
                str(len(p["achievements"]))]
    hab_lbls = list(l["hab"])
    hab_lbls[1] = hab_lbls[1] % m["boiled_sessions_pct"]
    hab_lbls[8] = hab_lbls[8] % (round(qt["how"]), round(qt["why"]))
    hab_tiles = "\n".join('<div class="tile"><b>%s</b><span>%s</span></div>' % (v, hab_lbls[i])
                          for i, v in enumerate(hab_vals) if v is not None)

    mm = [(l["models"].get(x["name"], x["name"]), x["count"]) for x in a["models"]]
    model_bars = "\n".join(bar_row(n, c, mm[0][1], BRASS, fmt(c)) for n, c in mm)
    ep = a["entrypoints"][0] if a["entrypoints"] else None
    ep_total = sum(x["count"] for x in a["entrypoints"]) or 1
    ts = a["top_sessions"][0] if a["top_sessions"] else None
    setup_vals = ["%s (%d%%)" % (l["ep"].get(ep["name"], ep["name"]),
                                 round(100.0 * ep["count"] / ep_total)) if ep else "?",
                  l["activations"] % m["plan_mode_count"],
                  str(a["versions_seen"]),
                  l["tokens_of"] % (ts["name"], fm(ts["tokens_out"])) if ts else "—"]
    setup_rows = "\n".join('<div class="kv"><span>%s</span><b>%s</b></div>' % (l["setup"][i], v)
                           for i, v in enumerate(setup_vals))

    top_ach = [x for x in p["achievements"] if x["rarity"] in ("legendary", "epic")]
    rest_ach = [x for x in p["achievements"] if x["rarity"] not in ("legendary", "epic")]
    if not top_ach:
        top_ach, rest_ach = rest_ach[:6], rest_ach[6:]
    chips = "\n".join(ach_card(x, l) for x in top_ach)
    accordion = ""
    if rest_ach:
        accordion = ('<details class="more"><summary>%s</summary>'
                     '<div class="chips" style="margin-top:10px">%s</div></details>'
                     % (l["more"] % len(rest_ach), "\n".join(ach_card(x, l) for x in rest_ach)))

    chron = "\n".join("<p>%s</p>" % x.strip().lstrip("<p>").rstrip("</p>") for x in content["chronicle"])
    strengths = content.get("strengths") or [l["balanced"]]
    strong = "\n".join("<li>%s</li>" % x for x in strengths[:3])
    fixes = "\n".join(
        '<div class="fix"><div class="w">%s</div><div class="a">→ %s</div><div class="ev">%s</div></div>'
        % (w["w"], w["a"], ('<a href="%s">%s</a>' % (w["url"], w["ev"])) if w.get("url") else w["ev"])
        for w in (content.get("weaknesses") or [])[:4])

    avatar_tag = '<img src="%s" alt="%s">\n' % (avatar, l["alt_avatar"]) if avatar else ""
    corpus = l["corpus"] % (fmt(m["messages"]), fmt(m["total_words"]), m["sessions"],
                            m["date_from"], m["date_to"], m["messages_per_active_day"])
    top_proj = a["top_projects"][0] if a["top_projects"] else {"name": "?", "share_pct": 0}

    return ("""<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8"><title>Prompt Warrior</title>%(favicon)s
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Cormorant+SC:wght@500;600;700&family=Cinzel:wght@500;600&family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>%(css)s</style></head><body><div class="card">

<div class="head">
%(avatar)s<div style="flex:1">
<div class="muted" style="font-family:'Cinzel','Cormorant SC',Georgia,serif;letter-spacing:.3em;font-size:10.5px">PROMPT WARRIOR</div>
<h1>%(h1)s</h1>
<div class="ident">%(ident)s</div>
<div class="muted" style="margin-top:6px">%(corpus)s</div>
</div>
<div class="lvl"><b>%(level)d</b><span>%(l_level)s</span></div>
</div>
<div class="dstrip">%(delta)s</div>

%(h_chron)s
<div class="chron">%(chron)s</div>

%(h_vol)s
<div class="grid">
<div class="tile"><b>%(v1)s</b><span>%(lv1)s</span></div>
<div class="tile"><b>%(v2)s</b><span>%(lv2)s</span></div>
<div class="tile"><b>%(v3)s%%</b><span>%(lv3)s</span></div>
<div class="tile"><b>%(v4)s%%</b><span>%(lv4)s</span></div>
</div>

<div class="cols">
<div>%(h_imp)s
%(imp)s</div>
<div>%(h_tone)s
%(tone)s</div>
</div>

<div class="duo">
<div>%(h_hours)s
<div class="hours">%(hours)s</div>
<div style="display:flex;justify-content:space-between;padding:0 8px" class="muted"><span>00</span><span>06</span><span>12</span><span>18</span><span>23</span></div></div>
<div>%(h_days)s
<div class="hours" style="gap:6px">%(days)s</div>
<div style="display:flex;justify-content:space-around;padding:0 8px" class="muted">%(days_lb)s</div></div>
</div>

%(h_gauges)s
<div class="g2">
%(gauges)s
</div>

%(h_eco)s
<div class="grid6">
<div class="tile"><b>%(e1)s</b><span>%(le1)s</span></div>
<div class="tile"><b>%(e2)s%%</b><span>%(le2)s</span></div>
<div class="tile"><b>%(e3)s</b><span>%(le3)s</span></div>
<div class="tile"><b>%(e4)s</b><span>%(le4)s</span></div>
<div class="tile"><b>%(e5)s</b><span>%(le5)s</span></div>
<div class="tile"><b>%(e6)s</b><span>%(le6)s</span></div>
</div>
<div class="cols">
<div><div class="h3">%(lh_tools)s</div>
%(tools)s</div>
<div><div class="h3">%(lh_roles)s</div>
%(cats)s</div>
</div>
<div class="cols">
<div><div class="h3">%(lh_mcp)s</div>
%(mcp)s</div>
<div><div class="h3">%(lh_ext)s</div>
%(ext)s</div>
</div>

%(h_hab)s
<div class="grid4">
%(hab)s
</div>
<div class="cols">
<div><div class="h3">%(lh_models)s</div>
%(models)s</div>
<div><div class="h3">%(lh_setup)s</div>
%(setup)s</div>
</div>

%(h_words)s
<div>%(words)s</div>

%(h_ach)s
<div class="chips">
%(chips)s
</div>
%(accordion)s

%(h_strong)s
<ul class="plus">
%(strong)s
</ul>

%(h_weak)s
%(fixes)s

<div class="foot muted"><span style="font-family:'Cinzel','Cormorant SC',Georgia,serif;letter-spacing:.15em;font-size:11px">SCALE %(scale)s</span><span class="seal">%(seal)s</span><span style="text-align:right">%(star)s<br><a href="https://github.com/timoncool/prompt-warrior">github.com/timoncool/prompt-warrior</a></span></div>
</div></body></html>""" % {
        "lang": lang, "favicon": icons.favicon(), "css": css_from_template(),
        "avatar": avatar_tag, "h1": h1,
        "ident": l["ident"] % (ident["class"][lang], ident["race"][lang], ident["race"]["share_pct"]),
        "corpus": corpus, "level": p["level"], "l_level": l["level"],
        "delta": delta_strip(p, l, content.get("delta_note")),
        "h_chron": h2(l, "chronicle"), "chron": chron,
        "h_vol": h2(l, "volume"),
        "v1": m["words_per_message"], "lv1": l["v_avg"],
        "v2": m["median_words_all"], "lv2": l["v_med"],
        "v3": m["quick_share_pct"], "lv3": l["v_short"],
        "v4": m["long_share_pct"], "lv4": l["v_spec"],
        "h_imp": h2(l, "imperatives"), "imp": imp_rows,
        "h_tone": h2(l, "tone"), "tone": tone_rows,
        "h_hours": h2(l, "hours"), "hours": hours,
        "h_days": h2(l, "days"), "days": days, "days_lb": days_lb,
        "h_gauges": h2(l, "gauges"), "gauges": gauges,
        "h_eco": h2(l, "economy"),
        "e1": fm(e["tokens_output"]), "le1": l["e_tok"],
        "e2": e["cache_efficiency_pct"], "le2": l["e_cache"],
        "e3": fmt(a["tool_calls"]), "le3": l["e_calls"],
        "e4": a["distinct_tools"], "le4": l["e_tools"],
        "e5": a["projects_count"], "le5": l["e_proj"] % (top_proj["name"], top_proj["share_pct"]),
        "e6": m["pr_count"], "le6": l["e_pr"],
        "lh_tools": l["h_tools"], "tools": tools_bars,
        "lh_roles": l["h_roles"], "cats": cats_bars,
        "lh_mcp": l["h_mcp"], "mcp": mcp_bars,
        "lh_ext": l["h_ext"], "ext": ext_bars,
        "h_hab": h2(l, "habits"), "hab": hab_tiles,
        "lh_models": l["h_models"], "models": model_bars,
        "lh_setup": l["h_setup"], "setup": setup_rows,
        "h_words": h2(l, "words"), "words": words,
        "h_ach": h2(l, "achievements"), "chips": chips, "accordion": accordion,
        "h_strong": h2(l, "strong", ' style="color:#A9BC6E"'), "strong": strong,
        "h_weak": h2(l, "weak", ' style="color:#D8A091"'), "fixes": fixes,
        "scale": p["scale_version"].upper(), "seal": icons.seal(), "star": l["star"],
    })


def main():
    ap = argparse.ArgumentParser(description="Prompt Warrior card renderer")
    ap.add_argument("profile")
    ap.add_argument("--content", required=True,
                    help="JSON with model-authored chronicle/strengths/weaknesses")
    ap.add_argument("--lang", choices=("ru", "en"), default="ru")
    ap.add_argument("--avatar", default="avatar.png",
                    help="avatar file next to the output (omitted if missing)")
    ap.add_argument("-o", "--output", default="ai-profile.html")
    args = ap.parse_args()

    p = json.load(open(args.profile, encoding="utf-8"))
    if "error" in p:
        raise SystemExit("profile has error: %s" % p["error"])
    content = json.load(open(args.content, encoding="utf-8"))
    if not content.get("chronicle") or not (2 <= len(content["chronicle"]) <= 4):
        raise SystemExit("content.chronicle must have 2-4 paragraphs (the model writes them)")

    avatar = args.avatar if os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(args.output)), args.avatar)) else None
    html = render(p, content, args.lang, avatar)
    assert "%(" not in html.replace("width:%d%%", ""), "unfilled slot"
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("written: %s (%d bytes, lang=%s, avatar=%s)" % (args.output, len(html), args.lang, bool(avatar)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
