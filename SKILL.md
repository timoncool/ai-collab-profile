---
name: prompt-warrior
description: Use when the user wants to analyze their communication style with AI from Claude Code logs — asks for a "prompt warrior" profile, an "AI profile", "wrapped", a psychological portrait of how they prompt, statistics of their sessions/messages, or personalized prompt-engineering recommendations based on their chat history. Works in any language (RU/EN lexicons built in).
---

# Prompt Warrior

Builds a gamified analytical portrait of the user's AI collaboration style from their
local Claude Code JSONL logs: real metrics on a FIXED scale (comparable between people)
plus fun statuses — a title, a level, achievements with rarity — and evidence-based
prompt-engineering recommendations. It is NOT an RPG character sheet:
no classes, no stat blocks; the analytics are the product, the statuses are the garnish.

**The scale is a contract.** All formulas and thresholds live in `scripts/analyze.py`
(SCALE v1) and `references/scale.md`. NEVER adjust formulas, thresholds, rank mappings,
or achievement conditions per user — comparability is the whole point. If a metric looks
unflattering, it stays. Report numbers only from `profile.json`, never invent or soften them.

## Workflow

1. **Run the analyzer** (Python 3, stdlib only, read-only — it never modifies logs):
   ```
   python scripts/analyze.py -o profile.json                        # all time, all projects
   python scripts/analyze.py --days 7 -o profile.json               # last week
   python scripts/analyze.py --days 30 -o profile.json              # last month
   python scripts/analyze.py --date-from 2026-06-01 --date-to 2026-06-30 -o profile.json
   python scripts/analyze.py --project <dir-name> -o profile.json   # one project
   ```
   THE RANGE IS THE USER'S CHOICE: if they named a period («за неделю», "this month",
   dates), pass it; if they didn't, default to all time and mention that a range is
   available. Never pick a range for the user silently.
   Default logs location: `~/.claude/projects`. Use `--projects-dir` to override.
   Try `python3` if `python` is missing.

2. **Read `profile.json`.**
   - `{"error": "not_enough_data"}` → tell the user at least 30 of their own messages are
     needed; stop.
   - `"low_confidence": true` (< 100 messages) → include a visible "small sample" caveat.

3. **Build the card from the template** in `references/widget.md` — fill it with
   profile.json data EXACTLY as the template prescribes: same CSS, same section order,
   strengths and weakness→fix pairs picked by the template's rules, every number
   printed exactly once. Write the result as `ai-profile.html` to the working
   directory and tell the user the path. If an inline widget tool is available,
   additionally render an inline widget mirroring the same sections and numbers.

4. **Explain the profile** in the user's conversation language (the widget carries both
   RU and EN labels from profile.json). Lead with what the numbers say — notable
   metrics, strengths and weaknesses; then the flavor: title (epithet + rank + level),
   achievements. Numbers verbatim from profile.json.

5. **Give recommendations** using `references/recommendations.md`: pick the entries whose
   trigger conditions match the profile, present 3-6 of them, each with its evidence note.
   Do not moralize about tone — research shows aggregate quality impact of tone is near
   zero; frame tone findings as fun facts plus practical notes (see recommendations.md).
   If the user asks about tone tricks, rudeness, tips/threats or "prompting lifehacks",
   use the Anti-myths section of recommendations.md — debunked claims with vote verdicts.

## Rules

- Read-only with respect to user logs. The only files written: `profile.json`, `ai-profile.html`.
- Respond in the user's language; RU/EN both supported end to end.
- Fixed scale: same formulas for everyone, always cite `SCALE v1` version in the card footer.
- Privacy: everything runs locally; nothing leaves the machine.
- If the user asks to compare with friends: they run the same skill; identical scale
  version = comparable results. Different scale versions are not comparable.
