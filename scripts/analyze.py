#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Warrior — analyzer (SCALE v1).

Reads Claude Code JSONL session logs, computes fixed-scale communication metrics,
derives fun statuses (rank, epithet, title, level, achievements) as flavor on top.
Stdlib only. Deterministic. RU/EN lexicons.

Usage:
  python analyze.py                          # all projects, ~/.claude/projects
  python analyze.py --project D--Projects-X  # one project dir
  python analyze.py -o profile.json          # write JSON (default: stdout)
"""
import argparse
import glob
import json
import math
import os
import re
import sys
from collections import Counter

SCALE_VERSION = "v1.4"  # v1..v1.3 без изменений; v1.4: +экономика токенов, арсенал, проекты, скриншоты, PR, plan-mode (слои поверх)

# ---------------------------------------------------------------- extraction

SYNTH_PREFIXES = (
    "Caveat:", "[Request interrupted", "This session is being continued",
    "<command-name>", "<local-command-stdout>", "<command-message>",
)
SYNTH_CONTAINS = (
    "<task-notification", "<command-name>", "<local-command-stdout>",
    "<ci-monitor-event>",
)


def extract_text(entry):
    """User-typed text from a JSONL entry, or None if synthetic/tool noise."""
    if entry.get("type") != "user" or entry.get("isMeta"):
        return None
    msg = entry.get("message") or {}
    if msg.get("role") != "user":
        return None
    content = msg.get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
    else:
        return None
    text = "\n".join(p for p in parts if p)
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S).strip()
    if not text:
        return None
    if any(text.startswith(p) for p in SYNTH_PREFIXES):
        return None
    if any(s in text for s in SYNTH_CONTAINS):
        return None
    return text


def new_aux():
    return {"interruptions": 0, "assistant_msgs": 0, "thinking": 0, "images": 0,
            "tool_errors": 0, "prs": 0, "plan_modes": 0, "queued": 0,
            "tok_in": 0, "tok_out": 0, "tok_cache_read": 0, "tok_cache_new": 0,
            "pr_urls": set(),
            "tools": Counter(), "models": Counter(), "projects": Counter()}


def harvest(entry, aux):
    """Дешёвые слои v1.4: токены, инструменты, модели, проекты, PR — из уже распарсенной строки."""
    t = entry.get("type")
    if t == "assistant":
        aux["assistant_msgs"] += 1
        msg = entry.get("message") or {}
        u = msg.get("usage") or {}
        for src, dst in (("input_tokens", "tok_in"), ("output_tokens", "tok_out"),
                         ("cache_read_input_tokens", "tok_cache_read"),
                         ("cache_creation_input_tokens", "tok_cache_new")):
            v = u.get(src)
            if isinstance(v, int):
                aux[dst] += v
        model = msg.get("model")
        if model and not str(model).startswith("<"):
            aux["models"][model] += 1
        c = msg.get("content")
        if isinstance(c, list):
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    aux["tools"][b.get("name", "?")] += 1
                elif b.get("type") == "thinking":
                    aux["thinking"] += 1
    elif t == "user":
        cwd = entry.get("cwd")
        if cwd:
            aux["projects"][cwd] += 1
        c = (entry.get("message") or {}).get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict):
                    if b.get("type") == "image":
                        aux["images"] += 1
                    elif b.get("type") == "tool_result" and b.get("is_error"):
                        aux["tool_errors"] += 1
    elif t == "pr-link":
        aux.setdefault("pr_urls", set()).add(entry.get("prUrl") or entry.get("prNumber") or "?")
    elif t == "mode":
        if entry.get("mode") == "plan":
            aux["plan_modes"] += 1
    elif t == "queue-operation":
        if entry.get("operation") == "enqueue":
            aux["queued"] += 1


def collect(projects_dir, project=None, aux=None):
    pattern = os.path.join(projects_dir, project or "*", "*.jsonl")
    files = [f for f in glob.glob(pattern)
             if not os.path.basename(f).startswith("agent-")
             and os.path.basename(f) != "journal.jsonl"]
    seen_uuid, seen_text = set(), set()
    if aux is not None:
        aux.update({k: v for k, v in new_aux().items() if k not in aux})
    messages = []  # dicts: text, words, voice, ts, session
    for path in files:
        session = os.path.basename(path)[:-6]
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if aux is not None:
                    harvest(entry, aux)
                text = extract_text(entry)
                if text is None:
                    if aux is not None and entry.get("type") == "user":
                        msg_ = entry.get("message") or {}
                        c_ = msg_.get("content")
                        t_ = c_ if isinstance(c_, str) else ""
                        if isinstance(c_, list):
                            t_ = " ".join(b.get("text", "") for b in c_ if isinstance(b, dict) and b.get("type") == "text")
                        if t_.startswith("[Request interrupted"):
                            aux["interruptions"] += 1
                    continue
                uid = entry.get("uuid")
                if uid and uid in seen_uuid:
                    continue
                if uid:
                    seen_uuid.add(uid)
                norm = re.sub(r"\s+", " ", text).lower()
                if norm in seen_text:
                    continue
                seen_text.add(norm)
                words = len(text.split())
                messages.append({
                    "text": text,
                    "words": words,
                    "voice": words <= 60 and "```" not in text and "http" not in text.lower(),
                    "ts": entry.get("timestamp") or "",
                    "session": session,
                })
    return messages


# ---------------------------------------------------------------- lexicons

LEX = {
    "imperative": re.compile(
        r"^(сдела|провер|запус[тк]|добав|давай$|убер|удал|исправ|поправ|почин|пофикс"
        r"|покаж|напиш|продолж|посмотр|глян|почитай|прочит|прочти|созда|измен|поменя"
        r"|закоммит|запуш|коммит$|пуш$|объясн|расскаж|попроб|верни|откат|останов|стоп$"
        r"|запиш|запомн|зафикс|протест|потест|найди|поищ|пройди|сравн|вывед|выгруз"
        r"|обнов|установ|постав|скажи|переделай|перезапус|собери|разбер"
        r"|make$|fix$|run$|add$|check$|create$|update$|remove$|delete$|show$|write$"
        r"|explain$|try$|revert$|stop$|find$|compare$|install$|build$|test$|deploy$)"
    ),
    "verify": re.compile(
        r"\b(провер\w*|убеди\w*|протест\w*|потест\w*|перепровер\w*|чекн\w*"
        r"|verify|double.?check|make sure|confirm)\b", re.I),
    "self_correction": re.compile(
        r"(\bстоп\b|\bпогоди\b|\bподожди\b|\bстой\b|\bотставить\b|\bотмена\b"
        r"|не то[,.! ]|я имел в виду|я ошиб\w+|\bвернись\b|не так[,.! ]"
        r"|\bwait\b|\bhold on\b|i meant|my bad|scratch that)", re.I),
    "politeness": re.compile(
        r"\b(пожалуйста|спасибо|благодарю|плиз|спс|please|thanks|thank you|thx)\b", re.I),
    "praise": re.compile(
        r"\b(красав\w*|молодец|отлично|супер|круто|заебись|огонь|шикарн\w*|прекрасно"
        r"|идеально|great|awesome|nice|perfect|excellent|well done)\b", re.I),
    "profanity": re.compile(
        r"\b(бля\w*|хуй\w*|хуе\w*|хуё\w*|нахуй|нихуя|охуе\w*|пизд\w*|еба\w*|ёба\w*"
        r"|ебё\w*|заеб\w*|доеб\w*|сука\w*|мудак\w*|говн\w*"
        r"|fuck\w*|shit\w*|damn|bullshit|wtf|crap)\b", re.I),
    "insult": re.compile(
        r"\b(идиот\w*|дебил\w*|долбо\w*|тупор\w*|туп(ая|ой|ица)|еблан\w*|уебан\w*"
        r"|у[её]б\w*|петух\w*|пидор\w*|мразь\w*|урод\w*|ублюдок\w*|придурок\w*"
        r"|кретин\w*|болван\w*|stupid|idiot|moron|dumbass|useless)\b", re.I),
    "why": re.compile(r"\b(почему|зачем|откуда|why|how come)\b", re.I),
    "memory_rules": re.compile(
        r"\b(запомни|запиши в память|в памят\w+|скилл\w*|рецепт\w*|в правил\w+"
        r"|remember this|add to memory|save this rule)\b", re.I),
    "categorical": re.compile(
        r"\b(всегда|никогда|только|обязательно|нельзя|запрещ\w*|ни в коем"
        r"|always|never|must|forbidden|do not ever)\b", re.I),
    "caps": re.compile(r"\b[А-ЯЁ]{4,}\b|\b[A-Z]{5,}\b"),
    "multipunct": re.compile(r"[?!]{3,}"),
    "question": re.compile(r"\?"),
    "structured": re.compile(r"```|https?://"),
}


IMPERATIVE_STEMS = [
    ("сделай", "make/do", re.compile(r"^(сдела|make$|do$)")),
    ("проверь", "check", re.compile(r"^(провер|перепровер|чекн|check$|verify)")),
    ("запусти", "run", re.compile(r"^(запус[тк]|перезапус|run$)")),
    ("добавь", "add", re.compile(r"^(добав|add$)")),
    ("давай", "let's go", re.compile(r"^давай$")),
    ("убери / удали", "remove", re.compile(r"^(убер|удал|remove$|delete$)")),
    ("исправь / почини", "fix", re.compile(r"^(исправ|поправ|почин|пофикс|fix$)")),
    ("стоп / останови", "stop", re.compile(r"^(останов|стоп$|stop$)")),
    ("покажи", "show", re.compile(r"^(покаж|show$)")),
    ("напиши", "write", re.compile(r"^(напиш|write$)")),
    ("обнови", "update", re.compile(r"^(обнов|update$)")),
    ("создай", "create", re.compile(r"^(созда|create$)")),
    ("найди", "find", re.compile(r"^(найди|поищ|find$|search$)")),
    ("установи / поставь", "install", re.compile(r"^(установ|постав|install$)")),
    ("верни / откати", "revert", re.compile(r"^(верни|откат|revert$)")),
    ("объясни", "explain", re.compile(r"^(объясн|расскаж|explain$)")),
]


def rate(messages, key):
    """Percent of messages matching lexicon key."""
    if not messages:
        return 0.0
    pat = LEX[key]
    return 100.0 * sum(1 for m in messages if pat.search(m["text"])) / len(messages)


# ---------------------------------------------------------------- metrics

def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


STOPWORDS = set(('''это этот эта что чтобы как когда где только если тоже также надо нужно можно нельзя есть быть был была было были будет
там тут здесь сейчас потом опять снова очень просто прямо давай давайте пусть пока ещё еще уже вот весь вся всё все всех даже
или либо ведь разве почему зачем какой какая какое какие такой такая такое такие него неё них тебя тебе меня мне нами вами
при про без над под перед после между через них наш ваш твой мой свой чтоб хочу хочешь хотим может можем должен должна должно
them they this that with have from были чего кого кому чему делать сделать делает работает работать файл файлы код кода коде
should would could there their about which после первый второй просто нормально правильно неправильно хорошо плохо
будем буду пожалуйста спасибо когда всегда никогда'''
).split())


def signature_words(voice, top_n=8):
    """Частотные слова юзера, не входящие в стоп-лист и лексиконы — «фирменный словарь»."""
    word_re = re.compile(r"[а-яёa-z]{4,}")
    counts = Counter()
    for m in voice:
        for tok in set(word_re.findall(m["text"].lower())):
            if tok in STOPWORDS or LEX["imperative"].match(tok):
                continue
            if any(LEX[k].search(tok) for k in ("profanity", "insult", "politeness", "praise", "verify")):
                continue
            counts[tok] += 1
    floor = max(5, len(voice) // 150)
    return [{"word": w, "count": c} for w, c in counts.most_common(top_n * 3) if c >= floor][:top_n]


def rage_marked(text):
    return bool(LEX["profanity"].search(text) or LEX["caps"].search(text) or LEX["multipunct"].search(text))


def compute_metrics(messages):
    voice = [m for m in messages if m["voice"]]
    n, nv = len(messages), len(voice)
    total_words = sum(m["words"] for m in messages) or 1
    lengths = sorted(m["words"] for m in voice) or [0]
    median_voice = lengths[len(lengths) // 2]
    all_lengths = sorted(m["words"] for m in messages) or [0]
    median_all = all_lengths[len(all_lengths) // 2]

    word_re = re.compile(r"[а-яёa-z]+")
    imperatives = 0
    stem_counts = Counter()
    for m in voice:
        for tok in word_re.findall(m["text"].lower()):
            if LEX["imperative"].match(tok):
                imperatives += 1
            for label_ru, label_en, pat in IMPERATIVE_STEMS:
                if pat.match(tok):
                    stem_counts[(label_ru, label_en)] += 1
                    break
    top_imperatives = [{"ru": ru, "en": en, "count": c}
                       for (ru, en), c in stem_counts.most_common(8)]

    profanity_hits = sum(len(LEX["profanity"].findall(m["text"])) for m in messages)

    days = Counter(m["ts"][:10] for m in messages if m["ts"])
    hours = Counter()
    for m in messages:
        hm = re.match(r"\d{4}-\d{2}-\d{2}T(\d{2})", m["ts"])
        if hm:
            hours[int(hm.group(1))] += 1
    total_ts = sum(hours.values()) or 1
    # night = local 00:00-05:59; timestamps are UTC, offset detected from local tz
    try:
        import datetime
        offset = round(-(__import__("time").timezone) / 3600)
    except Exception:
        offset = 0
    night = sum(c for h, c in hours.items() if 0 <= (h + offset) % 24 <= 5)
    hours_local = Counter()
    for h, c in hours.items():
        hours_local[(h + offset) % 24] += c
    morning = sum(c for h, c in hours_local.items() if 5 <= h <= 9)
    day = sum(c for h, c in hours_local.items() if 9 <= h <= 18)
    weekend = 0
    try:
        import datetime
        for msg in messages:
            if msg["ts"]:
                if datetime.date.fromisoformat(msg["ts"][:10]).weekday() >= 5:
                    weekend += 1
    except ValueError:
        pass
    span_days = 0
    if days:
        keys = sorted(days)
        try:
            from datetime import date
            d0 = date.fromisoformat(keys[0])
            d1 = date.fromisoformat(keys[-1])
            span_days = (d1 - d0).days + 1
        except ValueError:
            span_days = len(days)
    sessions = Counter(m["session"] for m in messages)
    negatives = sum(1 for m in messages
                    if LEX["insult"].search(m["text"]) or LEX["multipunct"].search(m["text"]))
    praise_n = sum(1 for m in messages if LEX["praise"].search(m["text"]))

    # точка кипения: номер первой реплики с маркером ярости, по сессиям (в порядке файла)
    per_session = {}
    for m in messages:
        per_session.setdefault(m["session"], []).append(m)
    boil_points = []
    boiled = 0
    for msgs_ in per_session.values():
        if len(msgs_) < 5:
            continue
        for idx, m in enumerate(msgs_, 1):
            if rage_marked(m["text"]):
                boil_points.append(idx)
                boiled += 1
                break
    rated_sessions = sum(1 for v in per_session.values() if len(v) >= 5)
    boil_points.sort()
    boiling_point = boil_points[len(boil_points) // 2] if boil_points else None

    # оборотень: мат ночью (00-06) против дня (09-18), по локальному часу
    def local_hour(m):
        hm = re.match(r"\d{4}-\d{2}-\d{2}T(\d{2})", m["ts"])
        return (int(hm.group(1)) + offset) % 24 if hm else None
    n_prof = d_prof = n_tot = d_tot = 0
    for m in messages:
        h = local_hour(m)
        if h is None:
            continue
        is_prof = bool(LEX["profanity"].search(m["text"]))
        if 0 <= h <= 5:
            n_tot += 1; n_prof += is_prof
        elif 9 <= h <= 18:
            d_tot += 1; d_prof += is_prof
    werewolf = None
    if n_tot >= 50 and d_tot >= 50 and d_prof:
        werewolf = round((n_prof / n_tot) / (d_prof / d_tot), 2)

    lang_base = voice or messages
    ru_chars = sum(len(re.findall(r"[а-яё]", m["text"].lower())) for m in lang_base)
    lat_chars = sum(len(re.findall(r"[a-z]", m["text"].lower())) for m in lang_base)

    return {
        "messages": n,
        "voice_messages": nv,
        "total_words": total_words,
        "words_per_message": round(total_words / n, 1) if n else 0,
        "median_words_voice": median_voice,
        "median_words_all": median_all,
        "sessions": len(sessions),
        "max_session_messages": max(sessions.values()) if sessions else 0,
        "active_days": len(days),
        "span_days": span_days,
        "messages_per_active_day": round(n / len(days), 1) if days else 0,
        "date_from": min(days) if days else None,
        "date_to": max(days) if days else None,
        "imperatives_per_100_voice": round(100.0 * imperatives / nv, 1) if nv else 0,
        "quick_share_pct": round(100.0 * sum(1 for m in voice if m["words"] <= 12) / nv, 1) if nv else 0,
        "long_share_pct": round(100.0 * sum(1 for m in messages if m["words"] >= 100) / n, 1) if n else 0,
        "structured_share_pct": round(rate(messages, "structured"), 1),
        "verify_pct": round(rate(messages, "verify"), 1),
        "self_correction_pct": round(rate(messages, "self_correction"), 1),
        "why_pct": round(rate(messages, "why"), 1),
        "question_pct": round(rate(messages, "question"), 1),
        "politeness_pct": round(rate(messages, "politeness"), 1),
        "praise_pct": round(rate(messages, "praise"), 1),
        "insult_pct": round(rate(messages, "insult"), 1),
        "profanity_per_1000_words": round(1000.0 * profanity_hits / total_words, 1),
        "profanity_msg_pct": round(rate(messages, "profanity"), 1),
        "caps_pct": round(rate(messages, "caps"), 1),
        "multipunct_pct": round(rate(messages, "multipunct"), 1),
        "categorical_pct": round(rate(messages, "categorical"), 1),
        "memory_rules_pct": round(rate(messages, "memory_rules"), 1),
        "night_share_pct": round(100.0 * night / total_ts, 1),
        "morning_share_pct": round(100.0 * morning / total_ts, 1),
        "day_share_pct": round(100.0 * day / total_ts, 1),
        "weekend_share_pct": round(100.0 * weekend / n, 1) if n else 0,
        "neg_to_praise_ratio": round(negatives / praise_n, 1) if praise_n else None,
        "language_mix": {"ru": round(100.0 * ru_chars / (ru_chars + lat_chars or 1)),
                         "en": round(100.0 * lat_chars / (ru_chars + lat_chars or 1))},
        "top_imperatives": top_imperatives,
        "hours_local": [hours_local.get(h, 0) for h in range(24)],
        "boiling_point_median": boiling_point,
        "boiled_sessions_pct": round(100.0 * boiled / rated_sessions, 1) if rated_sessions else 0,
        "werewolf_ratio": werewolf,
        "signature_words": signature_words(voice),
    }


# ---------------------------------------------------------------- SCALE v1
# Behavioral indexes (0-100, internal): used only to pick the fun rank; the card shows
# raw metrics, never these as a "stat sheet".

def compute_indexes(m):
    active_days_pct = 100.0 * m["active_days"] / m["span_days"] if m["span_days"] else 0
    indexes = {
        "command": clamp(m["imperatives_per_100_voice"] * 2),
        "tempo": clamp(m["quick_share_pct"] * 1.4),
        "endurance": clamp(0.35 * clamp(m["messages_per_active_day"])
                           + 0.35 * clamp(active_days_pct)
                           + 0.30 * clamp(m["night_share_pct"] * 2.5)),
        "context": clamp(0.4 * clamp(m["median_words_all"] * 2.5)
                         + 0.4 * clamp(m["long_share_pct"] * 20)
                         + 0.2 * clamp(m["structured_share_pct"] * 5)),
        "verification": clamp(0.5 * clamp(m["verify_pct"] * 6)
                              + 0.25 * clamp(m["self_correction_pct"] * 25)
                              + 0.25 * clamp(m["why_pct"] * 8)),
        "diplomacy": clamp(50 + m["politeness_pct"] * 10 + m["praise_pct"] * 5
                           - m["insult_pct"] * 2 - m["profanity_per_1000_words"] * 0.5),
    }
    indexes = {k: round(v) for k, v in indexes.items()}
    rage = round(clamp(m["profanity_per_1000_words"] * 1.5
                       + m["caps_pct"] + m["multipunct_pct"]))
    return indexes, rage


def compute_gauges(m, rage):
    """Fun 0-100 gauges. Derived from v1 metrics only; formulas frozen per version."""
    warmth = clamp(m["politeness_pct"] * 12 + m["praise_pct"] * 8)
    rigor = clamp(m["verify_pct"] * 6 + m["self_correction_pct"] * 10 + m["categorical_pct"] * 2)
    nocturnality = clamp(m["night_share_pct"] * 2.2)

    def bucket(value, hi, mid, lo, hi_t=60, mid_t=25):
        return hi if value >= hi_t else (mid if value >= mid_t else lo)

    return [
        {"id": "rage", "ru": "Ярость", "en": "Rage", "value": rage,
         "caption_ru": bucket(rage,
            "на качество ответов почти не влияет (агрегатный эффект тона ≈ 0 — arxiv 2508.00614, 2512.12812) — но жрёт токены без диагностики",
            "умеренный градус; тон почти не влияет на качество ответов (arxiv 2508.00614)",
            "дзен-режим: усилители (капс, мат, !!!) почти не используются"),
         "caption_en": bucket(rage,
            "barely affects response quality (aggregate tone effect ≈ 0 — arxiv 2508.00614, 2512.12812) — but burns tokens without diagnostics",
            "moderate heat; tone barely affects response quality (arxiv 2508.00614)",
            "zen mode: intensifiers (CAPS, profanity, !!!) are barely used")},
        {"id": "warmth", "ru": "Теплота", "en": "Warmth", "value": round(warmth),
         "caption_ru": bucket(warmth,
            "машины запомнят вас добром — похвала и вежливость как стиль",
            "тепло дозировано: похвала выдаётся за дело",
            "сухо и по делу — тоже стиль; похвала информативнее, чем кажется"),
         "caption_en": bucket(warmth,
            "the machines will remember you kindly — praise and courtesy as a style",
            "measured warmth: praise is earned",
            "dry and to the point — also a style; praise is more informative than it seems")},
        {"id": "rigor", "ru": "Дотошность", "en": "Rigor", "value": round(rigor),
         "caption_ru": bucket(rigor,
            "каждый вывод под присмотром: проверки, стопы, жёсткие рамки",
            "выборочный контроль: проверяете там, где дорого ошибиться",
            "работа на доверии — просите артефакты чаще, это дёшево"),
         "caption_en": bucket(rigor,
            "every output is supervised: checks, stops, hard constraints",
            "selective control: you verify where mistakes are expensive",
            "trust-based workflow — ask for artifacts more often, it is cheap")},
        {"id": "nocturnality", "ru": "Совиность", "en": "Nocturnality", "value": round(nocturnality),
         "caption_ru": bucket(nocturnality,
            "ночь — ваша смена: треть жизни с моделью проходит до рассвета",
            "сова наполовину: ночные вылазки случаются",
            "дневное существо: ночь для сна, редкий случай в этих логах"),
         "caption_en": bucket(nocturnality,
            "night is your shift: a third of your model time happens before dawn",
            "half an owl: night raids do happen",
            "daytime creature: nights are for sleep — rare in these logs")},
    ]


RANKS = {
    # dominant index -> fun rank (RU, EN)
    "command": ("Командир Терминала", "Terminal Commander"),
    "tempo": ("Мастер Молниеносных Правок", "Master of Lightning Edits"),
    "endurance": ("Марафонец Сессий", "Session Marathoner"),
    "context": ("Архитектор Спек", "Spec Architect"),
    "verification": ("Верховный Ревизор", "High Auditor"),
    "diplomacy": ("Дипломат Машин", "Machine Diplomat"),
}

INDEX_ORDER = ["command", "tempo", "endurance", "context", "verification", "diplomacy"]


def pick_rank(indexes):
    top = sorted(INDEX_ORDER, key=lambda k: (-indexes[k], INDEX_ORDER.index(k)))[0]
    return RANKS[top], top


def pick_epithet(m, rage):
    if rage >= 70:
        return ("Неистовый", "Furious")
    if m["night_share_pct"] >= 30:
        return ("Полуночный", "Midnight")
    if m["verify_pct"] >= 10:
        return ("Недоверчивый", "Skeptical")
    if m["politeness_pct"] >= 3:
        return ("Учтивый", "Courteous")
    if m["median_words_all"] >= 25:
        return ("Обстоятельный", "Thorough")
    if m["profanity_per_1000_words"] >= 30:
        return ("Сквернословящий", "Foul-mouthed")
    if m["morning_share_pct"] >= 25:
        return ("Рассветный", "Dawnbound")
    if m["verify_pct"] >= 6 and m["self_correction_pct"] >= 3:
        return ("Методичный", "Methodical")
    if m["median_words_voice"] <= 6:
        return ("Лаконичный", "Laconic")
    if m["praise_pct"] >= 8:
        return ("Щедрый", "Openhanded")
    return ("Странствующий", "Wandering")


RARITY_ORDER = {"common": 0, "rare": 1, "epic": 2, "legendary": 3}

ACHIEVEMENTS = [
    # (id, ru, en, rarity, suffix_ru, suffix_en, condition fn(m, rage))
    ("sprinter", "Спринтер", "Sprinter", "common", "Мастер короткой команды", "Master of the Short Command",
     lambda m, r: m["median_words_voice"] <= 8),
    ("novelist", "Романист", "Novelist", "rare", "Автор Великих Спек", "Author of Great Specs",
     lambda m, r: m["long_share_pct"] >= 3),
    ("trust_verify", "Доверяй, но проверяй", "Trust but Verify", "rare", "Око Ревизора", "Eye of the Auditor",
     lambda m, r: m["verify_pct"] >= 10),
    ("capslock", "Капслок-гладиатор", "Capslock Gladiator", "rare", "Голос Грома", "Voice of Thunder",
     lambda m, r: m["caps_pct"] >= 20),
    ("night_watch", "Ночной дозор", "Night's Watch", "rare", "Страж Полуночи", "Warden of Midnight",
     lambda m, r: m["night_share_pct"] >= 30),
    ("marathon", "Марафонец", "Marathoner", "epic", "Неутомимый", "The Tireless",
     lambda m, r: m["max_session_messages"] >= 300),
    ("eruption", "Извержение", "Eruption", "epic", "Гнев Вулкана", "Wrath of the Volcano",
     lambda m, r: m["profanity_per_1000_words"] >= 40),
    ("agent_bane", "Гроза агентов", "Bane of Agents", "epic", "Бич Ассистентов", "Scourge of Assistants",
     lambda m, r: m["insult_pct"] >= 20),
    ("surgeon", "Хирург", "Surgeon", "rare", "Твёрдая Рука", "The Steady Hand",
     lambda m, r: m["self_correction_pct"] >= 4),
    ("librarian", "Библиотекарь", "Librarian", "rare", "Хранитель Правил", "Keeper of Rules",
     lambda m, r: m["memory_rules_pct"] >= 3),
    ("sisyphus", "Сизиф", "Sisyphus", "rare", "Повелитель Откатов", "Lord of Rollbacks",
     lambda m, r: m["self_correction_pct"] + m["categorical_pct"] >= 8),
    ("tyrant", "Тиран", "Tyrant", "legendary", "Железная Длань", "The Iron Fist",
     lambda m, r: (m["neg_to_praise_ratio"] or 0) >= 10),
    ("saint", "Святой", "Saint", "legendary", "Светлейший", "The Radiant",
     lambda m, r: m["politeness_pct"] >= 5 and m["profanity_per_1000_words"] < 1),
    ("interrogator", "Дознаватель", "Interrogator", "common", "Задающий Вопросы", "Asker of Questions",
     lambda m, r: m["question_pct"] >= 30),
    ("why_child", "Почемучка", "The Why Child", "rare", "Искатель Причин", "Seeker of Causes",
     lambda m, r: m["why_pct"] >= 8),
    ("daily_grind", "Ежедневный гринд", "Daily Grind", "rare", "Верный Станку", "Loyal to the Forge",
     lambda m, r: m["span_days"] >= 14 and m["active_days"] / m["span_days"] >= 0.75),
    ("hundred_club", "Клуб ста", "Hundred Club", "common", "Столикий", "The Hundredfold",
     lambda m, r: m["messages"] >= 100),
    ("thousand_voices", "Тысяча голосов", "Thousand Voices", "rare", "Тысячеустый", "The Thousand-Tongued",
     lambda m, r: m["messages"] >= 1000),
    ("epic_wall", "Стена текста", "Wall of Text", "common", "Зодчий Абзацев", "Architect of Paragraphs",
     lambda m, r: m["words_per_message"] >= 30),
    ("polyglot", "Полиглот", "Polyglot", "rare", "Двуязыкий", "The Two-Tongued",
     lambda m, r: 25 <= m["language_mix"]["ru"] <= 75),
    ("zen", "Дзен", "Zen", "epic", "Невозмутимый", "The Unshaken",
     lambda m, r: r <= 5 and m["messages"] >= 300),
    ("volcano_heart", "Сердце вулкана", "Volcano Heart", "legendary", "Пламя Гнева", "Flame of Fury",
     lambda m, r: r >= 85),
    ("categorical_imperative", "Категорический императив", "Categorical Imperative", "rare",
     "Голос Абсолюта", "Voice of the Absolute",
     lambda m, r: m["categorical_pct"] >= 8),
    ("gentle_soul", "Добрая душа", "Gentle Soul", "rare", "Друг Машин", "Friend of Machines",
     lambda m, r: m["praise_pct"] >= 5),
    ("early_bird", "Ранняя пташка", "Early Bird", "rare", "Встречающий Рассвет", "Greeter of Dawns",
     lambda m, r: m["morning_share_pct"] >= 30),
    ("day_shift", "Дневная смена", "Day Shift", "common", "Хранитель Распорядка", "Keeper of the Schedule",
     lambda m, r: m["day_share_pct"] >= 55),
    ("weekender", "Воин выходных", "Weekend Warrior", "rare", "Не Знающий Суббот", "Knower of No Saturdays",
     lambda m, r: m["weekend_share_pct"] >= 35),
    ("verify_novice", "Ревизор-подмастерье", "Apprentice Auditor", "common", "Проверяющий", "The Checking One",
     lambda m, r: 5 <= m["verify_pct"] < 10),
    ("spec_architect", "Зодчий спецификаций", "Spec Architect", "epic", "Мастер Чертежей", "Master of Blueprints",
     lambda m, r: m["long_share_pct"] >= 8),
    ("calm_commander", "Спокойная сила", "Calm Command", "rare", "Невозмутимый Командир", "The Unruffled Commander",
     lambda m, r: m["imperatives_per_100_voice"] >= 30 and r < 20),
    ("diplomat", "Дипломат", "Diplomat", "rare", "Голос Согласия", "Voice of Accord",
     lambda m, r: m["politeness_pct"] >= 2 and m["insult_pct"] < 1),
    ("mentor", "Наставник", "Mentor", "epic", "Вдохновляющий", "The Inspiring",
     lambda m, r: m["praise_pct"] >= 10),
    ("decisive", "Без лишних вопросов", "No Questions Asked", "common", "Решительный", "The Decisive",
     lambda m, r: m["question_pct"] < 15 and m["messages"] >= 200),
    ("deep_diver", "Глубокое погружение", "Deep Diver", "rare", "Ныряющий в Детали", "Diver into Detail",
     lambda m, r: m["words_per_message"] >= 60),
    ("structured_mind", "Структурный ум", "Structured Mind", "rare", "Носитель Ссылок", "Bearer of References",
     lambda m, r: m["structured_share_pct"] >= 25),
    ("sprint_sessions", "Спринт-сессии", "Sprint Sessions", "common", "Мастер Коротких Заходов", "Master of Short Runs",
     lambda m, r: m["sessions"] >= 30 and m["messages"] / m["sessions"] <= 20),
    ("veteran", "Ветеран", "Veteran", "epic", "Старожил", "The Old Guard",
     lambda m, r: m["span_days"] >= 90),
    ("recruit", "Новобранец", "Recruit", "common", "Начинающий Путь", "Setting Out",
     lambda m, r: m["span_days"] <= 7),
    ("night_lord", "Владыка ночи", "Lord of the Night", "epic", "Повелитель Полуночи", "Sovereign of Midnight",
     lambda m, r: m["night_share_pct"] >= 50),
    ("balanced", "Уравновешенный", "Even Keel", "rare", "Держащий Баланс", "Holder of Balance",
     lambda m, r: 5 <= r <= 40 and (m["neg_to_praise_ratio"] or 0) <= 3 and m["messages"] >= 200),
    ("stop_cord", "Стоп-кран", "Emergency Brake", "rare", "Обрывающий на Полуслове", "Cutter of Mid-Sentences",
     lambda m, r: m.get("interruptions_per_100", 0) >= 8),
    ("patient_one", "Долготерпеливый", "The Patient One", "rare", "Дослушивающий", "The One Who Lets It Finish",
     lambda m, r: m.get("interruptions_per_100", 99) < 1 and m["messages"] >= 300),
    ("short_fuse", "Короткий фитиль", "Short Fuse", "epic", "Вспыхивающий Мгновенно", "The Instant Spark",
     lambda m, r: m.get("boiling_point_median") is not None and m["boiling_point_median"] <= 3),
    ("werewolf", "Оборотень", "Werewolf", "epic", "Меняющийся в Полночь", "The Midnight Turner",
     lambda m, r: (m.get("werewolf_ratio") or 0) >= 1.5),
    ("shipper", "Шиппер", "Shipper", "epic", "Доставляющий", "The One Who Ships",
     lambda m, r: m.get("pr_count", 0) >= 5),
    ("first_pr", "Первый PR", "First PR", "common", "Открывший Счёт", "First Blood on Main",
     lambda m, r: m.get("pr_count", 0) >= 1),
    ("screenshotter", "Скриншотер", "Screenshotter", "rare", "Показывающий, не Рассказывающий", "Shower, Not Teller",
     lambda m, r: m.get("images_per_100", 0) >= 3),
    ("cache_magnate", "Кэш-магнат", "Cache Magnate", "rare", "Повелитель Кэша", "Lord of the Cache",
     lambda m, r: (m.get("cache_efficiency_pct") or 0) >= 85),
    ("token_furnace", "Печатный станок", "Token Furnace", "epic", "Сжигающий Миллионы", "Burner of Millions",
     lambda m, r: m.get("tokens_output_m", 0) >= 5),
    ("planner", "Плановик", "The Planner", "rare", "Семь Раз Отмеряющий", "Measurer of Seven Times",
     lambda m, r: m.get("plan_mode_count", 0) >= 10),
    ("cowboy", "Ковбой", "Cowboy", "common", "Стреляющий с Бедра", "Shooter from the Hip",
     lambda m, r: m.get("plan_mode_count", 99) == 0 and m["sessions"] >= 50),
    ("multitool", "Мультитул", "Multitool", "rare", "Мастер Арсенала", "Master of the Arsenal",
     lambda m, r: m.get("distinct_tools", 0) >= 15),
    ("tool_breaker", "Ломатель", "Toolbreaker", "rare", "Испытатель Пределов", "Tester of Limits",
     lambda m, r: m.get("tool_error_pct", 0) >= 5),
]


ACHIEVEMENT_DESCS = {
    # id -> (флейвор RU, условие RU, flavor EN, condition EN)
    "sprinter": ("Слова — серебро: ваши команды укладываются в полдесятка слов",
                 "медиана набранной реплики ≤ 8 слов",
                 "Words are silver: your commands fit in half a dozen words",
                 "median typed message ≤ 8 words"),
    "novelist": ("Когда надо — выдаёте полноценные спеки, а не телеграммы",
                 "≥ 3% реплик длиннее 200 слов",
                 "When it matters, you deliver full specs, not telegrams",
                 "≥ 3% of messages over 200 words"),
    "trust_verify": ("На слово не верите: «проверь» — ваш рефлекс",
                     "запросы проверки в ≥ 10% реплик",
                     "You take nothing on faith: “verify” is your reflex",
                     "verify-requests in ≥ 10% of messages"),
    "capslock": ("КОГДА ВАЖНО, ВЫ ГОВОРИТЕ ВОТ ТАК",
                 "капс в ≥ 20% реплик",
                 "WHEN IT MATTERS, YOU SAY IT LIKE THIS",
                 "CAPS in ≥ 20% of messages"),
    "night_watch": ("Кодите, когда город спит — ночь и есть ваш рабочий день",
                    "≥ 30% активности между 00:00 и 06:00",
                    "You code while the city sleeps — night is your workday",
                    "≥ 30% of activity between midnight and 6 a.m."),
    "marathon": ("Сессии, которые не заканчиваются: вы уходите последним",
                 "одна сессия на 300+ реплик",
                 "Sessions that never end: you are the last to leave",
                 "a single session of 300+ messages"),
    "eruption": ("Обсценная лексика — полноправный рабочий инструмент",
                 "≥ 40 матов на 1000 слов",
                 "Profanity is a first-class working tool here",
                 "≥ 40 profanities per 1000 words"),
    "agent_bane": ("Ассистенты вздрагивают: каждая пятая реплика — с оскорблением",
                   "оскорбления в ≥ 20% реплик",
                   "Assistants flinch: every fifth message carries an insult",
                   "insults in ≥ 20% of messages"),
    "surgeon": ("Режете по живому вовремя: «стоп, не то» — до того, как стало поздно",
                "самокоррекция в ≥ 4% реплик",
                "You cut in time: “stop, wrong way” before it is too late",
                "self-correction in ≥ 4% of messages"),
    "librarian": ("Каждая ошибка становится правилом: память, скиллы, рецепты",
                  "≥ 3% реплик про память, правила и скиллы",
                  "Every mistake becomes a rule: memory, skills, recipes",
                  "≥ 3% of messages about memory, rules and skills"),
    "sisyphus": ("Стоп, откати, заново: камень регулярно катится с горы",
                 "стопы + категоричные требования ≥ 8% реплик",
                 "Stop, roll back, again: the boulder keeps coming down",
                 "stops + categorical demands ≥ 8% of messages"),
    "tyrant": ("Кнут вместо пряника: похвала — исчезающе редкий артефакт",
               "негативные сигналы превышают похвалу ≥ 10:1",
               "All stick, no carrot: praise is a vanishingly rare artifact",
               "negative signals outnumber praise ≥ 10:1"),
    "saint": ("Ни одного грубого слова — святость в мире дедлайнов",
              "вежливость ≥ 5% при мате < 1 на 1000 слов",
              "Not a single harsh word — sainthood in a world of deadlines",
              "politeness ≥ 5% with profanity < 1 per 1000 words"),
    "interrogator": ("Каждая третья реплика — вопрос: допрос с пристрастием",
                     "вопросы в ≥ 30% реплик",
                     "Every third message is a question: a proper interrogation",
                     "questions in ≥ 30% of messages"),
    "why_child": ("Вам нужен не фикс, а причина: докапываетесь до корня",
                  "«почему/зачем» в ≥ 8% реплик",
                  "You want the cause, not the patch: you dig to the root",
                  "why-questions in ≥ 8% of messages"),
    "daily_grind": ("Ни дня без строчки: станок не остывает",
                    "активность ≥ 75% дней на отрезке от двух недель",
                    "Not a day without a line: the forge never cools",
                    "active ≥ 75% of days over a 14+ day span"),
    "hundred_club": ("Первая сотня — самая важная",
                     "100+ реплик в корпусе",
                     "The first hundred is the one that counts",
                     "100+ messages in the corpus"),
    "thousand_voices": ("Корпус, с которым уже можно издавать собрание сочинений",
                        "1000+ реплик в корпусе",
                        "A corpus big enough for collected works",
                        "1000+ messages in the corpus"),
    "epic_wall": ("Реплики со смыслом и контекстом, а не междометия",
                  "в среднем ≥ 30 слов на реплику",
                  "Messages with substance and context, not interjections",
                  "≥ 30 words per message on average"),
    "polyglot": ("Живёте на два языка — и модель это чувствует",
                 "25–75% кириллицы в набранных репликах",
                 "You live in two languages — and the model feels it",
                 "typed messages 25–75% Cyrillic"),
    "zen": ("Триста реплик без единого всплеска — монастырская выдержка",
            "ярость ≤ 5 при 300+ репликах",
            "Three hundred messages without a single spike — monastic calm",
            "rage ≤ 5 across 300+ messages"),
    "volcano_heart": ("Клавиатура плавится: ярость на пределе шкалы",
                      "ярость ≥ 85 из 100",
                      "The keyboard melts: rage at the top of the scale",
                      "rage ≥ 85 out of 100"),
    "categorical_imperative": ("«Всегда» и «никогда» — ваши любимые кванторы",
                               "категоричные формулировки в ≥ 8% реплик",
                               "“Always” and “never” are your favourite quantifiers",
                               "categorical wording in ≥ 8% of messages"),
    "gentle_soul": ("Не скупитесь на «молодец» — редкий дар в этих краях",
                    "похвала в ≥ 5% реплик",
                    "Generous with praise — a rare gift in these lands",
                    "praise in ≥ 5% of messages"),
    "early_bird": ("Лучшие коммиты — до завтрака", "≥ 30% активности между 05:00 и 10:00",
                   "The best commits happen before breakfast", "≥ 30% of activity between 5 and 10 a.m."),
    "day_shift": ("Здоровый график — тоже суперспособность", "≥ 55% активности между 09:00 и 18:00",
                  "A sane schedule is a superpower too", "≥ 55% of activity between 9 a.m. and 6 p.m."),
    "weekender": ("Суббота — это просто пятница номер два", "≥ 35% реплик в выходные",
                  "Saturday is just a second Friday", "≥ 35% of messages on weekends"),
    "verify_novice": ("Проверка входит в привычку — уже не на слово", "запросы проверки в 5–10% реплик",
                      "Verification is becoming a habit", "verify-requests in 5-10% of messages"),
    "spec_architect": ("Постановки-чертежи: модель строит с первого раза", "≥ 8% реплик длиннее 200 слов",
                       "Blueprint briefs: the model builds it right the first time", "≥ 8% of messages over 200 words"),
    "calm_commander": ("Командуете много — не повышая голоса", "императивы ≥ 30 на 100 реплик при ярости < 20",
                       "Heavy command load without raising your voice", "imperatives ≥ 30/100 with rage < 20"),
    "diplomat": ("Вежливость без единого оскорбления — переговорщик от бога", "вежливость ≥ 2% при оскорблениях < 1%",
                 "Politeness with zero insults", "politeness ≥ 2% with insults < 1%"),
    "mentor": ("Каждая десятая реплика — поддержка: модель у вас работает лучше всех", "похвала в ≥ 10% реплик",
               "Every tenth message is encouragement", "praise in ≥ 10% of messages"),
    "decisive": ("Знаете, чего хотите — вопросы почти не нужны", "вопросы < 15% при 200+ репликах",
                 "You know what you want", "questions < 15% across 200+ messages"),
    "deep_diver": ("Реплики-эссе: каждая несёт полный контекст", "в среднем ≥ 60 слов на реплику",
                   "Essay-length messages carrying full context", "≥ 60 words per message on average"),
    "structured_mind": ("Код, ссылки, структура — модель получает материал, а не пересказ", "код или ссылки в ≥ 25% реплик",
                        "Code, links, structure in your messages", "code/links in ≥ 25% of messages"),
    "sprint_sessions": ("Забежал, сделал, вышел — десятки коротких точных сессий", "30+ сессий при ≤ 20 репликах на сессию",
                        "In, done, out: dozens of short precise sessions", "30+ sessions at ≤ 20 messages each"),
    "veteran": ("Три месяца в строю — это уже стиль жизни", "период активности ≥ 90 дней",
                "Three months in service", "activity span ≥ 90 days"),
    "recruit": ("Добро пожаловать на арену", "первая неделя в логах",
                "Welcome to the arena", "first week in the logs"),
    "night_lord": ("Не просто ночной дозор — ночь и есть ваша смена", "≥ 50% активности между 00:00 и 06:00",
                   "Night is not a watch, it is your shift", "≥ 50% of activity between midnight and 6 a.m."),
    "balanced": ("Ровный тон, ровный темп — редчайший профиль", "ярость 5–40, негатив к похвале ≤ 3, от 200 реплик",
                 "Even tone, even tempo", "rage 5-40, negativity:praise <= 3 across 200+ messages"),
    "stop_cord": ("Модель ещё пишет, а вы уже знаете, что не то", "≥ 8 прерываний на 100 реплик",
                  "The model is still typing, but you already know it is wrong", "≥ 8 interruptions per 100 messages"),
    "patient_one": ("Дослушиваете до конца — даже когда не согласны", "< 1 прерывания на 100 реплик при 300+ репликах",
                    "You let it finish, even when you disagree", "< 1 interruption per 100 messages across 300+"),
    "short_fuse": ("Искра — с третьей реплики сессии", "медианная первая вспышка ≤ 3-й реплики сессии",
                   "The spark comes by message three", "median first flare-up at message ≤ 3 of a session"),
    "werewolf": ("После полуночи вами пишет кто-то другой", "ночной мат чаще дневного в ≥ 1.5 раза",
                 "Someone else types through you after midnight", "night profanity ≥ 1.5x the daytime rate"),
    "shipper": ("Сессии кончаются пулл-реквестами, а не разговорами", "≥ 5 PR из сессий",
                "Sessions end in pull requests, not conversations", "≥ 5 PRs born from sessions"),
    "first_pr": ("Первый PR из сессии — дальше пойдёт легче", "≥ 1 PR из сессий",
                 "First PR from a session", "≥ 1 PR born from a session"),
    "screenshotter": ("Зачем описывать, если можно показать", "≥ 3 картинки на 100 реплик",
                      "Why describe when you can show", "≥ 3 images per 100 messages"),
    "cache_magnate": ("Контекст переиспользуется, а не оплачивается заново", "кэш-чтения ≥ 85% входного контекста",
                      "Context is reused, not repurchased", "cache reads ≥ 85% of input context"),
    "token_furnace": ("Миллионы токенов выхода — производство не останавливается", "≥ 5 млн токенов сгенерировано",
                      "Millions of output tokens — production never stops", "≥ 5M output tokens generated"),
    "planner": ("Сначала план, потом код — и так десять раз подряд", "план-режим ≥ 10 раз",
                "Plan first, code second — ten times over", "plan mode entered ≥ 10 times"),
    "cowboy": ("План-режим? Не слышал", "0 включений план-режима при 50+ сессиях",
               "Plan mode? Never heard of it", "0 plan-mode entries across 50+ sessions"),
    "multitool": ("В арсенале больше инструментов, чем у иного цеха", "≥ 15 разных инструментов в ходу",
                  "More tools in rotation than some whole teams", "≥ 15 distinct tools used"),
    "tool_breaker": ("Инструменты не выдерживают темпа", "≥ 5% вызовов инструментов с ошибкой",
                     "The tools cannot keep up", "≥ 5% of tool calls error out"),
}


def compute_achievements(m, rage):
    earned = []
    for aid, ru, en, rarity, suf_ru, suf_en, cond in ACHIEVEMENTS:
        try:
            ok = bool(cond(m, rage))
        except Exception:
            ok = False
        if ok:
            flavor_ru, cond_ru, flavor_en, cond_en = ACHIEVEMENT_DESCS.get(aid, ("", "", "", ""))
            earned.append({"id": aid, "ru": ru, "en": en, "rarity": rarity,
                           "suffix_ru": suf_ru, "suffix_en": suf_en,
                           "desc_ru": flavor_ru, "cond_ru": cond_ru,
                           "desc_en": flavor_en, "cond_en": cond_en})
    earned.sort(key=lambda a: -RARITY_ORDER[a["rarity"]])
    return earned


TOOL_CATS = {
    "operator": ("Bash", "PowerShell"),
    "surgeon": ("Edit", "Write", "NotebookEdit"),
    "archaeologist": ("Read", "Grep", "Glob"),
}


def build_layers(aux, n_messages):
    """Опциональные слои v1.4 (экономика/арсенал) — если источник их отдал."""
    if not aux or not aux.get("assistant_msgs"):
        return None, None
    tok_in, tok_out = aux["tok_in"], aux["tok_out"]
    cache_read, cache_new = aux["tok_cache_read"], aux["tok_cache_new"]
    context_total = tok_in + cache_read
    economy = {
        "tokens_output": tok_out,
        "tokens_input_fresh": tok_in,
        "tokens_cache_read": cache_read,
        "tokens_cache_creation": cache_new,
        "cache_efficiency_pct": round(100.0 * cache_read / context_total, 1) if context_total else None,
        "assistant_messages": aux["assistant_msgs"],
        "thinking_blocks": aux["thinking"],
    }
    total_tools = sum(aux["tools"].values())
    cats = {}
    for cat, names in TOOL_CATS.items():
        cats[cat] = round(100.0 * sum(aux["tools"].get(n, 0) for n in names) / total_tools, 1) if total_tools else 0
    mcp_calls = sum(c for n, c in aux["tools"].items() if n.startswith("mcp__"))
    proj_total = sum(aux["projects"].values())
    top_projects = [{"name": os.path.basename(n.rstrip("\\/")) or n, "share_pct": round(100.0 * c / proj_total, 1)}
                    for n, c in aux["projects"].most_common(5)] if proj_total else []
    arsenal = {
        "tool_calls": total_tools,
        "distinct_tools": len(aux["tools"]),
        "top_tools": [{"name": n, "count": c} for n, c in aux["tools"].most_common(8)],
        "category_shares_pct": cats,
        "mcp_share_pct": round(100.0 * mcp_calls / total_tools, 1) if total_tools else 0,
        "models": [{"name": n, "count": c} for n, c in aux["models"].most_common(5)],
        "projects_count": len(aux["projects"]),
        "top_projects": top_projects,
        "tool_error_pct": round(100.0 * aux["tool_errors"] / total_tools, 1) if total_tools else 0,
    }
    return economy, arsenal


def build_profile(messages, aux=None):
    m = compute_metrics(messages)
    n_int = (aux or {}).get("interruptions", 0)
    m["interruptions"] = n_int
    m["interruptions_per_100"] = round(100.0 * n_int / m["messages"], 1) if m["messages"] else 0
    economy, arsenal = build_layers(aux, m["messages"])
    m["images_per_100"] = round(100.0 * (aux or {}).get("images", 0) / m["messages"], 1) if m["messages"] else 0
    m["pr_count"] = len((aux or {}).get("pr_urls", set()))
    m["plan_mode_count"] = (aux or {}).get("plan_modes", 0)
    m["tool_error_pct"] = arsenal["tool_error_pct"] if arsenal else 0
    m["distinct_tools"] = arsenal["distinct_tools"] if arsenal else 0
    m["cache_efficiency_pct"] = economy["cache_efficiency_pct"] if economy else None
    m["tokens_output_m"] = round(economy["tokens_output"] / 1e6, 1) if economy else 0
    if m["messages"] < 30:
        return {"error": "not_enough_data", "messages": m["messages"],
                "note": "Need at least 30 user messages for a profile."}
    indexes, rage = compute_indexes(m)
    (rank_ru, rank_en), top_index = pick_rank(indexes)
    ep_ru, ep_en = pick_epithet(m, rage)
    level = max(1, min(99, int(math.sqrt(m["total_words"]) / 5)))
    achievements = compute_achievements(m, rage)
    suffix = achievements[0] if achievements else None
    title_ru = "%s %s %d уровня" % (ep_ru, rank_ru, level)
    title_en = "%s %s, level %d" % (ep_en, rank_en, level)
    if suffix and RARITY_ORDER[suffix["rarity"]] >= 2:
        title_ru += ", " + suffix["suffix_ru"]
        title_en += ", " + suffix["suffix_en"]
    return {
        "scale_version": SCALE_VERSION,
        "low_confidence": m["messages"] < 100,
        "metrics": m,
        "indexes": indexes,
        "rage": rage,
        "rank": {"ru": rank_ru, "en": rank_en, "key": top_index},
        "epithet": {"ru": ep_ru, "en": ep_en},
        "level": level,
        "title": {"ru": title_ru, "en": title_en},
        "achievements": achievements,
        "gauges": compute_gauges(m, rage),
        "economy": economy,
        "arsenal": arsenal,
    }


def filter_by_range(messages, days=None, date_from=None, date_to=None):
    """Keep messages inside the requested window (dates are the ts date part)."""
    if days:
        dates = sorted({m["ts"][:10] for m in messages if m["ts"]})
        if dates:
            import datetime
            last = datetime.date.fromisoformat(dates[-1])
            date_from = (last - datetime.timedelta(days=days - 1)).isoformat()
            date_to = dates[-1]
    if not date_from and not date_to:
        return messages
    lo = date_from or "0000-00-00"
    hi = date_to or "9999-99-99"
    return [m for m in messages if m["ts"] and lo <= m["ts"][:10] <= hi]


HISTORY_PATH = os.path.expanduser(os.path.join("~", ".claude", "prompt-warrior", "history.jsonl"))

SNAPSHOT_METRICS = ["messages", "total_words", "median_words_voice", "verify_pct",
                    "self_correction_pct", "politeness_pct", "praise_pct",
                    "profanity_per_1000_words", "insult_pct", "caps_pct",
                    "night_share_pct", "long_share_pct", "question_pct"]


def load_history():
    try:
        with open(HISTORY_PATH, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
    except (OSError, json.JSONDecodeError):
        return []


def compute_delta(profile, history):
    """Compare against the previous all-time snapshot; None on first run."""
    if not history:
        return None
    prev = history[-1]
    m = profile["metrics"]
    cur_ach = {a["id"] for a in profile["achievements"]}
    new_ach = [a for a in profile["achievements"] if a["id"] not in set(prev.get("achievements", []))]
    metric_changes = {}
    for key in SNAPSHOT_METRICS:
        was = prev.get("metrics", {}).get(key)
        now = m.get(key)
        if was is not None and now is not None and was != now:
            metric_changes[key] = {"from": was, "to": now}
    return {
        "since": prev.get("date"),
        "runs_recorded": len(history),
        "level": {"from": prev.get("level"), "to": profile["level"]},
        "rage": {"from": prev.get("rage"), "to": profile["rage"]},
        "title_changed": prev.get("title_ru") != profile["title"]["ru"],
        "prev_title": prev.get("title_ru"),
        "messages_added": m["messages"] - prev.get("metrics", {}).get("messages", m["messages"]),
        "new_achievements": new_ach,
        "lost_achievements": sorted(set(prev.get("achievements", [])) - cur_ach),
        "metric_changes": metric_changes,
    }


def append_snapshot(profile):
    m = profile["metrics"]
    snap = {
        "date": m["date_to"],
        "scale_version": profile["scale_version"],
        "level": profile["level"],
        "rage": profile["rage"],
        "title_ru": profile["title"]["ru"],
        "achievements": [a["id"] for a in profile["achievements"]],
        "metrics": {k: m[k] for k in SNAPSHOT_METRICS},
    }
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    history = load_history()
    if history and history[-1].get("date") == snap["date"]:
        history[-1] = snap  # повторный прогон в тот же день — заменить, не плодить
    else:
        history.append(snap)
    with open(HISTORY_PATH, "w", encoding="utf-8") as fh:
        for item in history:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- sources
# Адаптеры харнессов: каждый источник = функция(dir, project) -> messages.
# Сейчас реализован Claude Code; форматы OpenCode/Codex/Copilot/Gemini — по мере
# верификации их логов (см. README, Cross-harness).
SOURCES = {
    "claude-code": {
        "collect": lambda d, proj, aux=None: collect(d, proj, aux),
        "default_dir": os.path.join("~", ".claude", "projects"),
    },
}


def main():
    ap = argparse.ArgumentParser(description="Prompt Warrior analyzer (SCALE %s)" % SCALE_VERSION)
    ap.add_argument("--source", choices=sorted(SOURCES), default="claude-code",
                    help="which harness logs to read (default: claude-code)")
    ap.add_argument("--projects-dir", default=None)
    ap.add_argument("--project", default=None, help="single project dir name (default: all)")
    ap.add_argument("--days", type=int, default=None,
                    help="last N days (7 = week, 30 = month); default: all time")
    ap.add_argument("--date-from", default=None, help="YYYY-MM-DD, inclusive")
    ap.add_argument("--date-to", default=None, help="YYYY-MM-DD, inclusive")
    ap.add_argument("-o", "--output", default=None, help="write JSON to file (default: stdout)")
    ap.add_argument("--no-history", action="store_true",
                    help="do not read/write the local progress history")
    args = ap.parse_args()

    src = SOURCES[args.source]
    logs_dir = args.projects_dir or os.path.expanduser(src["default_dir"])
    aux = {}
    messages = src["collect"](logs_dir, args.project, aux)
    messages = filter_by_range(messages, args.days, args.date_from, args.date_to)
    profile = build_profile(messages, aux)
    if "metrics" in profile:
        profile["range"] = {"days": args.days, "from": args.date_from, "to": args.date_to,
                            "mode": ("last_%d_days" % args.days) if args.days
                                    else ("custom" if (args.date_from or args.date_to) else "all_time")}
        # прогресс между визитами: только для сравнимых all-time прогонов
        if profile["range"]["mode"] == "all_time" and not args.no_history:
            history = load_history()
            profile["delta"] = compute_delta(profile, history)
            append_snapshot(profile)
    out = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
        print("written: %s (%d messages analyzed)" % (args.output, profile.get("metrics", {}).get("messages", 0)))
    else:
        print(out)


if __name__ == "__main__":
    main()
