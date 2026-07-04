#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Collab Profile — analyzer (SCALE v1).

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

SCALE_VERSION = "v1"

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


def collect(projects_dir, project=None):
    pattern = os.path.join(projects_dir, project or "*", "*.jsonl")
    files = [f for f in glob.glob(pattern)
             if not os.path.basename(f).startswith("agent-")
             and os.path.basename(f) != "journal.jsonl"]
    seen_uuid, seen_text = set(), set()
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
                text = extract_text(entry)
                if text is None:
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
        "neg_to_praise_ratio": round(negatives / praise_n, 1) if praise_n else None,
        "language_mix": {"ru": round(100.0 * ru_chars / (ru_chars + lat_chars or 1)),
                         "en": round(100.0 * lat_chars / (ru_chars + lat_chars or 1))},
        "top_imperatives": top_imperatives,
        "hours_local": [hours_local.get(h, 0) for h in range(24)],
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
]


def compute_achievements(m, rage):
    earned = []
    for aid, ru, en, rarity, suf_ru, suf_en, cond in ACHIEVEMENTS:
        try:
            ok = bool(cond(m, rage))
        except Exception:
            ok = False
        if ok:
            earned.append({"id": aid, "ru": ru, "en": en, "rarity": rarity,
                           "suffix_ru": suf_ru, "suffix_en": suf_en})
    earned.sort(key=lambda a: -RARITY_ORDER[a["rarity"]])
    return earned


def build_profile(messages):
    m = compute_metrics(messages)
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


def main():
    ap = argparse.ArgumentParser(description="AI Collab Profile analyzer (SCALE %s)" % SCALE_VERSION)
    ap.add_argument("--projects-dir", default=os.path.expanduser(os.path.join("~", ".claude", "projects")))
    ap.add_argument("--project", default=None, help="single project dir name (default: all)")
    ap.add_argument("--days", type=int, default=None,
                    help="last N days (7 = week, 30 = month); default: all time")
    ap.add_argument("--date-from", default=None, help="YYYY-MM-DD, inclusive")
    ap.add_argument("--date-to", default=None, help="YYYY-MM-DD, inclusive")
    ap.add_argument("-o", "--output", default=None, help="write JSON to file (default: stdout)")
    args = ap.parse_args()

    messages = collect(args.projects_dir, args.project)
    messages = filter_by_range(messages, args.days, args.date_from, args.date_to)
    profile = build_profile(messages)
    if "metrics" in profile:
        profile["range"] = {"days": args.days, "from": args.date_from, "to": args.date_to,
                            "mode": ("last_%d_days" % args.days) if args.days
                                    else ("custom" if (args.date_from or args.date_to) else "all_time")}
    out = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
        print("written: %s (%d messages analyzed)" % (args.output, profile.get("metrics", {}).get("messages", 0)))
    else:
        print(out)


if __name__ == "__main__":
    main()
