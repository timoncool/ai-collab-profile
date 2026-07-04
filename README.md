# AI Collab Profile

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-8b5cf6)](https://code.claude.com/docs/en/skills)
[![Scale](https://img.shields.io/badge/scale-v1-blue)](references/scale.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)](scripts/analyze.py)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![RU/EN](https://img.shields.io/badge/lang-RU%20%2F%20EN-orange)](#русский)

Turn your Claude Code history into a gamified analytical portrait. The skill analyzes
your local session logs and shows how you actually work with AI — real numbers on a
**fixed scale** (comparable between people), a fun title, a level, achievements with
rarity, and evidence-based prompt-engineering recommendations.
Not an RPG character sheet: the analytics are the product, the statuses are the garnish.

> **Furious Terminal Commander, level 89, The Iron Fist** — rage 82/100 · «проверь» is imperative #2 · negativity:praise 24:1

## Install

```bash
git clone https://github.com/timoncool/ai-collab-profile ~/.claude/skills/ai-collab-profile
```

Windows (PowerShell):

```powershell
git clone https://github.com/timoncool/ai-collab-profile "$env:USERPROFILE\.claude\skills\ai-collab-profile"
```

That's it. Python 3.8+ (stdlib only), no dependencies, no API keys, no network calls.

## Use

In any Claude Code session:

```
/ai-collab-profile
```

or just ask: *"построй мой AI-профиль"* / *"build my AI collaboration profile"* —
optionally with a period: *"за неделю"*, *"for the last month"*, *"с 1 по 30 июня"*.
Default is all time; the range is always your choice (`--days N`, `--date-from/--date-to`).

You get one card — a serious analytical portrait with RPG flavor woven in:
- **The analytics** (the substance): volume, top imperatives, tone markers, activity by
  hour, strengths and weaknesses derived strictly from your numbers;
- **The statuses** (the garnish): fun title as the headline (epithet + rank + level),
  the rage gauge, up to 24 achievements (common → legendary);
- **3-6 personalized recommendations**, each backed by published research or Anthropic docs
  (see [references/recommendations.md](references/recommendations.md));
- Inline widget + self-contained `ai-profile.html` you can open, screenshot and share.

## Fair play

The scale is a contract: formulas and thresholds are frozen per version
([SCALE v1](references/scale.md)). Everyone is measured identically — that's what makes
profiles comparable. Yes, even if your rage gauge hits 82/100.

## Privacy

Everything runs locally; nothing ever leaves your machine.

---

## Русский

Скилл для Claude Code: геймифицированный аналитический портрет вашего стиля работы с ИИ.
Локальный анализ логов → реальные цифры по **фиксированной шкале** (сравнимой между
людьми), прикольный титул, уровень, ачивки с редкостью и рекомендации по
промпт-инженерингу с опорой на исследования. Это не RPG-лист персонажа: аналитика —
продукт, статусы — приправа.

**Установка:** команда `git clone` выше (папка `~/.claude/skills/ai-collab-profile`).
Нужен только Python 3.8+, без зависимостей и ключей.

**Запуск:** `/ai-collab-profile` или просто «построй мой AI-профиль» в любой сессии.

**Честная игра:** формулы шкалы заморожены ([SCALE v1](references/scale.md)) — все
измеряются одинаково, поэтому профили можно сравнивать. Да, даже если градус ярости — 82.

**Приватность:** всё локально; наружу не уходит ничего.

## Structure

```
SKILL.md                       # skill entry: triggers + workflow
scripts/analyze.py             # analyzer (stdlib-only, deterministic, read-only)
references/scale.md            # SCALE v1 — frozen formulas
references/rpg.md              # fun statuses: ranks, epithets, achievements
references/recommendations.md  # metric-triggered advice with sources
references/widget.md           # полный шаблон карточки для модели + правила дедупа
references/sources.md          # verified evidence links (and refuted claims)
```
