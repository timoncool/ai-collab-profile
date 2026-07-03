# AI Collab Profile

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-8b5cf6)](https://code.claude.com/docs/en/skills)
[![Scale](https://img.shields.io/badge/scale-v1-blue)](references/scale.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)](scripts/analyze.py)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![RU/EN](https://img.shields.io/badge/lang-RU%20%2F%20EN-orange)](#русский)

Turn your Claude Code history into an RPG character sheet. The skill analyzes your local
session logs and builds a psychological portrait of how you work with AI — six D&D-style
stats on a **fixed scale** (comparable between people), a class, a title, achievements
with rarity, an avatar, and evidence-based prompt-engineering recommendations.

> **Furious Barbarian, level 89, The Iron Fist** — STR 93 · CON 90 · DEX 79 · WIS 45 · INT 41 · CHA 4 · RAGE 81

## Install

```bash
git clone https://github.com/timoncool/ai-collab-profile ~/.claude/skills/ai-collab-profile
```

Windows (PowerShell):

```powershell
git clone https://github.com/timoncool/ai-collab-profile "$env:USERPROFILE\.claude\skills\ai-collab-profile"
```

That's it. Python 3.8+ (stdlib only), no dependencies, no API keys.

## Use

In any Claude Code session:

```
/ai-collab-profile
```

or just ask: *"построй мой AI-профиль"* / *"build my AI collaboration profile"*.

You get:
- **Character card** — inline widget + self-contained `ai-profile.html` you can open,
  screenshot and share;
- **Six stats** — STR directiveness, DEX iteration tempo, CON intensity, INT context
  richness, WIS verification, CHA diplomacy — plus the RAGE meter;
- **Class of 15** (top-2 stats), epithet, level, up to 24 achievements (common → legendary);
- **Avatar** — procedural SVG out of the box; optional AI avatar via [Puter.js](https://developer.puter.com/)
  (no developer keys, user-pays model);
- **3-6 personalized recommendations**, each backed by published research or Anthropic docs
  (see [references/recommendations.md](references/recommendations.md)).

## Fair play

The scale is a contract: formulas and thresholds are frozen per version
([SCALE v1](references/scale.md)). Everyone is measured identically — that's what makes
profiles comparable. Yes, even if your CHA turns out to be 4.

## Privacy

Everything runs locally; log content never leaves your machine. The optional AI avatar
sends only a short generated prompt (class/epithet words) to the image service.

---

## Русский

Скилл для Claude Code: превращает историю ваших сессий в RPG-лист персонажа. Локальный
анализ логов → психологический портрет стиля работы с ИИ: шесть статов по **фиксированной
шкале** (сравнимой между людьми), класс, титул, ачивки с редкостью, аватар и рекомендации
по промпт-инженерингу с опорой на исследования.

**Установка:** команда `git clone` выше (папка `~/.claude/skills/ai-collab-profile`).
Нужен только Python 3.8+, без зависимостей и ключей.

**Запуск:** `/ai-collab-profile` или просто «построй мой AI-профиль» в любой сессии.

**Честная игра:** формулы шкалы заморожены ([SCALE v1](references/scale.md)) — все
измеряются одинаково, поэтому профили можно сравнивать. Да, даже если ваша Харизма — 4.

**Приватность:** всё локально; наружу может уйти только короткий промпт аватара
(слова класса и эпитета), и только по явной кнопке.

## Structure

```
SKILL.md                       # skill entry: triggers + workflow
scripts/analyze.py             # analyzer (stdlib-only, deterministic, read-only)
references/scale.md            # SCALE v1 — frozen formulas
references/rpg.md              # classes, epithets, achievements
references/recommendations.md  # metric-triggered advice with sources
references/widget.md           # card render spec + avatar recipes
```
