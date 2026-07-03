---
name: ai-collab-profile
description: Use when the user wants to analyze their communication style with AI from Claude Code logs — asks for an "AI profile", "RPG profile", "wrapped", a psychological portrait of how they prompt, statistics of their sessions/messages, or personalized prompt-engineering recommendations based on their chat history. Works in any language (RU/EN lexicons built in).
---

# AI Collab Profile

Builds an RPG-style character sheet of the user's AI collaboration style from their local
Claude Code JSONL logs: six D&D-like stats on a FIXED scale (comparable between people),
a class, an epithet, a title, a level, achievements with rarity, an avatar, and
evidence-based prompt-engineering recommendations.

**The scale is a contract.** All formulas and thresholds live in `scripts/analyze.py`
(SCALE v1) and `references/scale.md`. NEVER adjust formulas, thresholds, class mappings,
or achievement conditions per user — comparability is the whole point. If a metric looks
unflattering, it stays. Report numbers only from `profile.json`, never invent or soften them.

## Workflow

1. **Run the analyzer** (Python 3, stdlib only, read-only — it never modifies logs):
   ```
   python scripts/analyze.py -o profile.json            # all projects
   python scripts/analyze.py --project <dir-name> -o profile.json   # one project
   ```
   Default logs location: `~/.claude/projects`. Use `--projects-dir` to override.
   Try `python3` if `python` is missing.

2. **Read `profile.json`.**
   - `{"error": "not_enough_data"}` → tell the user at least 30 of their own messages are
     needed; stop.
   - `"low_confidence": true` (< 100 messages) → include a visible "small sample" caveat.

3. **Render the character card** following `references/widget.md`:
   - If an inline widget tool is available in this environment, render it inline.
   - Always also write a self-contained `ai-profile.html` to the working directory and
     tell the user the path (they can open it in a browser and screenshot/share it).
   - The card includes a procedural SVG avatar (recipe in widget.md) that always works
     offline. The HTML file additionally offers an optional AI-avatar button via Puter.js
     (no developer keys; the user signs into a free Puter account — user-pays model).
     Use `avatar_prompt` from profile.json for the image prompt.

4. **Explain the profile** in the user's conversation language (the widget carries both
   RU and EN labels from profile.json). Walk through: title, class and what drove it
   (top-2 stats), the most notable metrics behind each stat, achievements earned.
   Numbers verbatim from profile.json.

5. **Give recommendations** using `references/recommendations.md`: pick the entries whose
   trigger conditions match the profile, present 3-6 of them, each with its evidence note.
   Do not moralize about tone — research shows aggregate quality impact of tone is near
   zero; frame tone findings as fun facts plus practical notes (see recommendations.md).

## Rules

- Read-only with respect to user logs. The only files written: `profile.json`, `ai-profile.html`.
- Respond in the user's language; RU/EN both supported end to end.
- Fixed scale: same formulas for everyone, always cite `SCALE v1` version in the card footer.
- Privacy: everything runs locally; no log content leaves the machine. The optional AI
  avatar sends ONLY the generated `avatar_prompt` string (class/epithet words, no log text)
  to the image service — say this to the user when they use it.
- If the user asks to compare with friends: they run the same skill; identical scale
  version = comparable results. Different scale versions are not comparable.
