<div align="center">

# Prompt Warrior

**Turn your Claude Code logs into a gamified analytical portrait of how you work with AI.**

[![License](https://img.shields.io/github/license/timoncool/prompt-warrior?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/timoncool/prompt-warrior?style=flat-square)](https://github.com/timoncool/prompt-warrior/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/timoncool/prompt-warrior?style=flat-square)](https://github.com/timoncool/prompt-warrior/commits)
[![Python](https://img.shields.io/badge/python-3.8%2B%20stdlib--only-3776AB?style=flat-square)](scripts/analyze.py)

**[English](README.md)** · **[Русский](README_RU.md)**

![Prompt Warrior card](docs/screenshots/hero.png)

</div>

Prompt Warrior is a Claude Code skill that analyzes your local session logs and shows how
you actually communicate with AI — real numbers on a fixed scale, comparable between
people. You get a shareable card with your stats, a fun title, achievements with rarity,
and research-backed prompting advice. Runs 100% locally on stdlib Python, nothing ever
leaves your machine.

## Features

- **Fixed scale (SCALE v1)** — frozen formulas and thresholds, everyone is measured identically, profiles are comparable
- **Real analytics** — message volume, top imperatives, tone markers, activity by hour, strengths and weak spots derived strictly from your numbers
- **Fun statuses** — a title built from your behavior (epithet + rank + level), 24 achievements from common to legendary, the rage gauge
- **Research-backed advice** — every recommendation cites a verified source; refuted claims are listed too ([sources.md](references/sources.md))
- **Progress between visits** — the skill remembers your last run (locally): come back in a week and see new achievements, level-ups and metric shifts
- **Duel a friend** — exchange `profile.json` files and run `scripts/compare.py` for a versus card; the fixed scale makes it fair
- **Deep-cut signals** — interruption rate, session boiling point, the werewolf index (night vs day profanity), your signature vocabulary
- **Economy & arsenal** — tokens burned and cache efficiency, your tool profile (operator / surgeon / archaeologist), models, projects, PRs shipped
- **Cross-harness aware** — known session-log formats for Codex CLI, OpenCode, Gemini CLI and Copilot documented in [references/harnesses.md](references/harnesses.md)
- **Any period** — all time by default, or last week, last month, exact dates: your choice
- **100% local and private** — stdlib-only Python, zero dependencies, no API keys, no network calls
- **RU / EN** — lexicons and output in both languages

## Quick Start

1. **Clone**
   ```bash
   git clone https://github.com/timoncool/prompt-warrior ~/.claude/skills/prompt-warrior
   ```
   Windows (PowerShell):
   ```powershell
   git clone https://github.com/timoncool/prompt-warrior "$env:USERPROFILE\.claude\skills\prompt-warrior"
   ```
   or install as a plugin:
   ```
   /plugin marketplace add timoncool/prompt-warrior
   /plugin install prompt-warrior@prompt-warrior
   ```

2. **Ask Claude Code**
   ```
   /prompt-warrior
   ```
   or just say: *"build my prompt warrior profile"*.

3. **Get your card** — an inline widget plus a self-contained `ai-profile.html` you can
   open, screenshot and share.

## Usage

- *"build my prompt warrior profile"* — all-time profile
- *"my prompt profile for the last week"* — last 7 days
- *"профиль за июнь"* — exact date range
- The period is always your choice; the skill never picks one silently.

Under the hood: `scripts/analyze.py` reads `~/.claude/projects` JSONL logs (read-only),
deduplicates your messages, computes metrics and writes `profile.json`; Claude then
builds the card from the template in [references/widget.md](references/widget.md).

## Documentation

- [SCALE v1 — frozen formulas](references/scale.md)
- [Ranks, epithets, achievements](references/rpg.md)
- [Metric-triggered recommendations](references/recommendations.md)
- [Evidence base with verification verdicts](references/sources.md)

## Other Projects by [@timoncool](https://github.com/timoncool)

| Project | Description |
|---------|-------------|
| [telegram-api-mcp](https://github.com/timoncool/telegram-api-mcp) | Full Telegram Bot API as MCP server |
| [civitai-mcp-ultimate](https://github.com/timoncool/civitai-mcp-ultimate) | Civitai API as MCP server |
| [trail-spec](https://github.com/timoncool/trail-spec) | TRAIL — cross-MCP content tracking protocol |
| [GitLife](https://github.com/timoncool/gitlife) | Your life in weeks — interactive calendar |
| [ACE-Step Studio](https://github.com/timoncool/ACE-Step-Studio) | AI music studio — songs, vocals, covers, videos |
| [VideoSOS](https://github.com/timoncool/videosos) | AI video production in the browser |

## Authors

- **Nerual Dreming** — [Telegram](https://t.me/nerual_dreming) | [neuro-cartel.com](https://neuro-cartel.com) | [ArtGeneration.me](https://artgeneration.me)

## Support the Author

I build open-source software and do AI research. Most of what I create is free and available to everyone. Your donations help me keep creating without worrying about where the next meal comes from =)

**[All donation methods](https://github.com/timoncool/ACE-Step-Studio/blob/master/DONATE.md)** | **[dalink.to/nerual_dreming](https://dalink.to/nerual_dreming)** | **[boosty.to/neuro_art](https://boosty.to/neuro_art)**

- **BTC:** `1E7dHL22RpyhJGVpcvKdbyZgksSYkYeEBC`
- **ETH (ERC20):** `0xb5db65adf478983186d4897ba92fe2c25c594a0c`
- **USDT (TRC20):** `TQST9Lp2TjK6FiVkn4fwfGUee7NmkxEE7C`

## Star History

<a href="https://www.star-history.com/?repos=timoncool%2Fprompt-warrior&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=timoncool/prompt-warrior&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=timoncool/prompt-warrior&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=timoncool/prompt-warrior&type=date&legend=top-left" />
 </picture>
</a>

## License

[MIT](LICENSE)
