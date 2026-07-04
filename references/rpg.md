# Fun statuses — ranks, epithets, achievements

Геймификация без RPG-цирка: никаких классов и стат-листов. Прикольный титул, уровень,
ачивки с редкостью — приправа к аналитике. Это не вкусовщина, а проверенный паттерн:
Stack Overflow прямо описывает бейджи как «dusting of gamification» по модели Xbox
Achievements — щепотка, а не ядро продукта (stackoverflow.blog, vote 3-0). Все условия зафиксированы в
`scripts/analyze.py` (SCALE v1); тут — справочник для рендера и нарратива.

## Title

`{Эпитет} {Звание} {N} уровня[, {суффикс топ-ачивки}]`
`{Epithet} {Rank}, level {N}[, {top achievement suffix}]`

Суффикс добавляется только если самая редкая ачивка — epic или legendary.
Пример: «Неистовый Командир Терминала 89 уровня, Железная Длань».

## Rank — звание по доминирующему поведению

Выбирается по наибольшему внутреннему поведенческому индексу (см. scale.md);
tie-break по порядку строк:

| Индекс | RU | EN |
|--------|----|----|
| command (директивность) | Командир Терминала | Terminal Commander |
| tempo (темп правок) | Мастер Молниеносных Правок | Master of Lightning Edits |
| endurance (марафоны) | Марафонец Сессий | Session Marathoner |
| context (спеки) | Архитектор Спек | Spec Architect |
| verification (проверки) | Верховный Ревизор | High Auditor |
| diplomacy (вежливость) | Дипломат Машин | Machine Diplomat |

## Epithet (первое сработавшее условие)

| Condition | RU | EN |
|-----------|----|----|
| RAGE ≥ 70 | Неистовый | Furious |
| night share ≥ 30% | Полуночный | Midnight |
| verify ≥ 10% | Недоверчивый | Skeptical |
| politeness ≥ 3% | Учтивый | Courteous |
| median words ≥ 25 | Обстоятельный | Thorough |
| profanity ≥ 30/1000 | Сквернословящий | Foul-mouthed |
| morning ≥ 25% | Рассветный | Dawnbound |
| verify ≥ 6% и самокоррекция ≥ 3% | Методичный | Methodical |
| median ≤ 6 слов | Лаконичный | Laconic |
| praise ≥ 8% | Щедрый | Openhanded |
| default | Странствующий | Wandering |

## Achievements (41, редкость по паттерну bronze/silver/gold + legendary)

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
| early_bird | Ранняя пташка | Early Bird | rare | ≥ 30% активности 05:00–10:00 |
| day_shift | Дневная смена | Day Shift | common | ≥ 55% активности 09:00–18:00 |
| weekender | Воин выходных | Weekend Warrior | rare | ≥ 35% реплик в выходные |
| verify_novice | Ревизор-подмастерье | Apprentice Auditor | common | verify 5–10% (ступень к Trust but Verify) |
| spec_architect | Зодчий спецификаций | Spec Architect | epic | ≥ 8% реплик 200+ слов (ступень от Романиста) |
| calm_commander | Спокойная сила | Calm Command | rare | императивы ≥ 30/100 при ярости < 20 |
| diplomat | Дипломат | Diplomat | rare | вежливость ≥ 2% при оскорблениях < 1% |
| mentor | Наставник | Mentor | epic | похвала ≥ 10% (ступень от Доброй души) |
| decisive | Без лишних вопросов | No Questions Asked | common | вопросы < 15% при 200+ репликах |
| deep_diver | Глубокое погружение | Deep Diver | rare | ≥ 60 слов на реплику в среднем |
| structured_mind | Структурный ум | Structured Mind | rare | код/ссылки в ≥ 25% реплик |
| sprint_sessions | Спринт-сессии | Sprint Sessions | common | 30+ сессий по ≤ 20 реплик |
| veteran | Ветеран | Veteran | epic | период ≥ 90 дней |
| recruit | Новобранец | Recruit | common | первая неделя в логах |
| night_lord | Владыка ночи | Lord of the Night | epic | ночь ≥ 50% (ступень от Ночного дозора) |
| balanced | Уравновешенный | Even Keel | rare | ярость 5–40, негатив:похвала ≤ 3 |

Принцип прогрессии (по модели GitHub Achievements с тирами Bronze/Silver/Gold): часть ачивок
образует лестницы — «Клуб ста» → «Тысяча голосов» (объём), «Спринтер» → «Романист» (стиль).
Новые ачивки добавлять предпочтительно ступенями к существующим, а не одиночками.

Нарратив: сначала legendary/epic, в конце 1-2 самых смешных common. Не стыдить —
ачивки это флейвор, включая «Тирана» (см. recommendations.md про влияние тона).
