# Widget — character card render spec

Two render targets, same content:
1. **Inline widget** (if the environment has one, e.g. show_widget) — follow host design
   system, light layout of the same sections.
2. **`ai-profile.html`** (always) — self-contained dark-fantasy card, template below.
   No external deps except the optional Puter.js script. Works offline (avatar = SVG).

Language: render labels in the user's conversation language (profile.json has ru/en pairs).
Numbers verbatim from profile.json. Footer must show `SCALE v1 · ai-collab-profile`.

## Sections (in order)

1. **Header**: avatar (left) + title, class ru/en, level badge, corpus line
   (messages · words · sessions · date range; add "low confidence" ribbon if flagged).
2. **Stats**: six horizontal bars (STR/DEX/CON/INT/WIS/CHA), value 0-100, one accent color,
   short human meaning under each label (e.g. STR — директивность).
3. **Rage meter**: separate thin bar, gradient green→red, with a one-line fun caption.
4. **Achievements**: grid of cards; rarity border colors — common #9aa0a6, rare #3b82f6,
   epic #a855f7, legendary #f59e0b; rarity label + RU/EN name; earned only.
5. **Key numbers**: 4-6 metric tiles (median words, verify %, profanity/1000, night %,
   msgs/day, neg:praise ratio — pick the most characterful for this profile).
6. **Recommendations**: 3-6 from references/recommendations.md, numbered, one line each
   (details go in the chat message, not the card).
7. **Footer**: `SCALE v1 · ai-collab-profile · github.com/timoncool/ai-collab-profile`.

## Procedural SVG avatar (default, always works)

Deterministic from profile: 160×160 SVG —
- outer ring: stroke = top-stat color (STR #e05252, DEX #52b788, CON #d97706, INT #3b82f6,
  WIS #8b5cf6, CHA #ec4899), thickness 6, with `stroke-dasharray` gap pattern from level;
- background: radial dark (#1a1625 → #0d0b12); night epithet → add 3-4 small star dots;
- center: class initial (first letter of EN class), serif, 64px, color of the ring;
- bottom badge: level number in a small rhombus;
- if rarest achievement is legendary → faint outer glow (#f59e0b at 25% opacity).

## Optional AI avatar (Puter.js, no developer keys)

Button «Сгенерировать AI-аватар / Generate AI avatar» inside the HTML card. On click,
disclose: prompt only (no log content) goes to the image service; user signs into a free
Puter account on first use (user-pays model). Verified call format:

```html
<script src="https://js.puter.com/v2/"></script>
<script>
async function genAvatar() {
  const img = await puter.ai.txt2img(AVATAR_PROMPT, { model: "black-forest-labs/flux-2-pro" });
  img.style.cssText = "width:160px;height:160px;object-fit:cover;border-radius:12px";
  document.getElementById("avatar").replaceChildren(img);
}
</script>
```

`AVATAR_PROMPT` = `avatar_prompt` from profile.json. If the call fails (offline, no account),
keep the SVG and show a quiet note — never block the card on it.

## HTML template skeleton

Dark card 720px, system fonts, no frameworks:

```html
<!doctype html><html><head><meta charset="utf-8"><title>AI Collab Profile</title><style>
body{background:#0d0b12;color:#e8e4f0;font:15px/1.6 system-ui,sans-serif;display:flex;justify-content:center;padding:24px}
.card{width:720px;background:#161221;border:1px solid #2a2438;border-radius:16px;padding:28px}
h1{font-size:24px;margin:0}.muted{color:#8d86a3;font-size:13px}
.bar{height:12px;background:#241e33;border-radius:6px;overflow:hidden}
.bar>i{display:block;height:100%;background:#8b5cf6;border-radius:6px}
.ach{border:1px solid;border-radius:10px;padding:8px 12px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.tile{background:#1d1830;border-radius:10px;padding:10px 14px}
.rage{height:8px;border-radius:4px;background:linear-gradient(90deg,#22c55e,#eab308,#ef4444)}
</style></head><body><div class="card"><!-- sections 1-7 --></div></body></html>
```

Fill with real values; bar width = stat value %. Keep total file < 40 KB.
