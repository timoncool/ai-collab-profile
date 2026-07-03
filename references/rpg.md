# RPG system — classes, epithets, achievements

Все условия зафиксированы в `scripts/analyze.py` (SCALE v1). Тут — справочник для
рендера и объяснений. / All conditions are frozen in `analyze.py`; this is the render
and narration reference.

## Class = top-2 stats (15 combinations)

| Top-2 | RU | EN | Flavor |
|-------|----|----|--------|
| STR+DEX | Берсерк | Berserker | быстрые короткие команды, шквал директив |
| STR+CON | Варвар | Barbarian | напор + марафоны, сила через объём |
| STR+INT | Полководец | Warlord | командует развёрнутыми приказами |
| STR+WIS | Инквизитор | Inquisitor | приказывает и проверяет каждый шаг |
| STR+CHA | Паладин | Paladin | директивен, но учтив |
| DEX+CON | Следопыт | Ranger | быстрые итерации день за днём |
| DEX+INT | Плут | Rogue | короткие точные уколы с контекстом |
| DEX+WIS | Монах | Monk | быстрый, но осознанный |
| DEX+CHA | Бард | Bard | лёгкий тон, быстрый темп |
| CON+INT | Артификер | Artificer | долгие сессии над большими спеками |
| CON+WIS | Друид | Druid | выносливость + рефлексия |
| CON+CHA | Вождь | Chieftain | ведёт долго и дипломатично |
| INT+WIS | Архимаг | Archmage | глубокий контекст + верификация |
| INT+CHA | Чародей | Sorcerer | богатый контекст, мягкая подача |
| WIS+CHA | Клирик | Cleric | проверяет и благодарит |

Tie-break: при равенстве статов приоритет по порядку STR, DEX, CON, INT, WIS, CHA.

## Epithet (first match wins)

| Condition | RU | EN |
|-----------|----|----|
| RAGE ≥ 70 | Неистовый | Furious |
| night share ≥ 30% | Полуночный | Midnight |
| verify ≥ 10% | Недоверчивый | Skeptical |
| politeness ≥ 3% | Учтивый | Courteous |
| median words ≥ 25 | Обстоятельный | Thorough |
| profanity ≥ 30/1000 | Сквернословящий | Foul-mouthed |
| default | Странствующий | Wandering |

## Title

`{Epithet} {Class} {level} уровня` / `{Epithet} {Class}, level {level}`;
if the rarest earned achievement is epic or legendary, its suffix is appended
(e.g. «Железная Длань» / "The Iron Fist").

## Achievements (24, by rarity)

Rarity tiers follow the proven bronze/silver/gold pattern (Stack Overflow) extended with
legendary: **common → rare → epic → legendary**.

| ID | RU | EN | Rarity | Condition |
|----|----|----|--------|-----------|
| sprinter | Спринтер | Sprinter | common | median voice message ≤ 8 words |
| hundred_club | Клуб ста | Hundred Club | common | ≥ 100 messages |
| interrogator | Дознаватель | Interrogator | common | questions ≥ 30% |
| epic_wall | Стена текста | Wall of Text | common | avg words/message ≥ 30 |
| novelist | Романист | Novelist | rare | ≥ 3% messages of 200+ words |
| trust_verify | Доверяй, но проверяй | Trust but Verify | rare | verify ≥ 10% |
| capslock | Капслок-гладиатор | Capslock Gladiator | rare | CAPS ≥ 20% |
| night_watch | Ночной дозор | Night's Watch | rare | night share ≥ 30% |
| surgeon | Хирург | Surgeon | rare | self-correction ≥ 4% |
| librarian | Библиотекарь | Librarian | rare | memory/rules ≥ 3% |
| sisyphus | Сизиф | Sisyphus | rare | self-corr + categorical ≥ 8% |
| why_child | Почемучка | The Why Child | rare | why ≥ 8% |
| daily_grind | Ежедневный гринд | Daily Grind | rare | ≥ 75% active days over ≥ 14-day span |
| thousand_voices | Тысяча голосов | Thousand Voices | rare | ≥ 1000 messages |
| polyglot | Полиглот | Polyglot | rare | voice language mix 25–75% RU |
| categorical_imperative | Категорический императив | Categorical Imperative | rare | categorical ≥ 8% |
| gentle_soul | Добрая душа | Gentle Soul | rare | praise ≥ 5% |
| marathon | Марафонец | Marathoner | epic | a session with ≥ 300 messages |
| eruption | Извержение | Eruption | epic | profanity ≥ 40/1000 words |
| agent_bane | Гроза агентов | Bane of Agents | epic | insults ≥ 20% |
| zen | Дзен | Zen | epic | RAGE ≤ 5 with ≥ 300 messages |
| tyrant | Тиран | Tyrant | legendary | negativity : praise ≥ 10:1 |
| saint | Святой | Saint | legendary | politeness ≥ 5% and profanity < 1/1000 |
| volcano_heart | Сердце вулкана | Volcano Heart | legendary | RAGE ≥ 85 |

Narration tip: legendary/epic first, mention 1-2 funniest common ones last. Never shame —
achievements are flavor, including Tyrant and Eruption (see recommendations.md for tone facts).
