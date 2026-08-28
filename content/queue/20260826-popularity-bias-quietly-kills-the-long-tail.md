---
id: 20260826-ef0d185d
slug: popularity-bias-quietly-kills-the-long-tail
pillar: hot_take
status: skipped
created: 2026-08-26T05:47:01+00:00
idea: Most 'diversity' fixes trade measurable CTR for unmeasured retention, which is why they get rolled back.  Why now:
source_url: local://seed/9a7c3d7ed29c
variant: 
tg_message_id: 83
rewrite_note: 
post_urn: 
published_at: 
material_ref: local://seed/9a7c3d7ed29c
skip_reason: no answer within 44h
---

<!-- variant_a -->
CTR = clicks / impressions. A diversity intervention is usually judged on that ratio, while its intended benefit may appear later as retention.

That mismatch is why many diversity fixes get rolled back.

Popularity bias creates a feedback loop: popular items receive more exposure, accumulate more interactions, and become even easier for the ranker to recommend. The long tail is not necessarily irrelevant; it is simply given fewer chances to produce evidence.

A diversity reranker interrupts this loop by moving some less-exposed items into visible positions. Those items often have lower predicted click probability than the popular alternatives they replace.

So the immediate delta is easy to see:

ΔCTR < 0

The possible retention delta is harder to attribute:

Δretention > 0, but delayed and confounded.

If the decision rule is “ship only when CTR improves,” rollback is the mathematically consistent outcome. The problem is not that diversity lost. It was evaluated against a metric that captures its cost but not its intended return.

My position: do not call diversity a ranking feature. Treat it as a product investment with a measurement window long enough to observe whether the long tail creates repeat behavior.

<!-- variant_b -->
Diversity is not usually rolled back because it fails. It is rolled back because teams expect it to win a CTR comparison it was designed to lose.

A ranker trained on observed interactions learns from exposure that was already concentrated around popular items. More exposure produces more clicks; more clicks produce stronger training signals; stronger signals produce still more exposure.

That is popularity bias as a feedback loop.

A diversity constraint breaks the loop by reserving some prominent positions for items with less historical evidence. In the short term, this can replace a high predicted-click item with one the model knows less about.

The online result is straightforward:

ΔCTR < 0

But the intended result is not “more clicks on this impression.” It is a catalog that remains discoverable, with more reasons for users to return over time.

If retention is measured later, on another cohort, or not connected to the ranking experiment at all, then only one side of the trade-off enters the rollout decision. CTR is a measured cost. Retention is an unmeasured promise.

The fix is not to demand that diversity beat popularity on immediate CTR. It is to decide explicitly whether long-tail discovery is worth a short-term ranking cost, then measure the answer on that horizon.

<!-- ru_a -->
CTR = клики / показы. Diversity intervention обычно оценивают по этому соотношению, хотя ожидаемый эффект от неё может проявиться позже в retention.

Именно из-за этого несоответствия многие diversity-изменения откатывают.

Popularity bias создаёт feedback loop: популярные items получают больше показов, накапливают больше взаимодействий и становятся ещё более удобными для рекомендаций ranker’а. Long tail не обязательно нерелевантен — ему просто дают меньше шансов накопить evidence.

Diversity reranker прерывает этот цикл, перемещая некоторые items с меньшим числом показов на видимые позиции. У таких items часто ниже predicted click probability, чем у популярных альтернатив, которые они заменяют.

Поэтому immediate delta легко увидеть:

ΔCTR < 0

А delta retention сложнее атрибутировать:

Δretention > 0, но с задержкой и под влиянием confounders.

Если decision rule звучит как «выкатывать только при улучшении CTR», rollback становится математически закономерным результатом. Проблема не в том, что diversity проиграла. Её оценивали по метрике, которая отражает её стоимость, но не предполагаемый эффект.

Моя позиция: не называйте diversity ranking feature. Относитесь к ней как к product investment с measurement window, достаточно длинным, чтобы увидеть, формирует ли long tail повторное поведение.

<!-- ru_b -->
Разнообразие обычно откатывают не потому, что оно не работает. Его откатывают потому, что команды ожидают, что оно выиграет сравнение по CTR, в котором изначально должно было проиграть.

Ранжировщик, обученный на наблюдаемых взаимодействиях, учится на экспозиции, которая уже была сконцентрирована вокруг популярных items. Больше экспозиции даёт больше кликов; больше кликов — более сильные обучающие сигналы; более сильные сигналы — ещё больше экспозиции.

Это и есть popularity bias, работающий как feedback loop.

Ограничение на diversity разрывает этот цикл, резервируя некоторые заметные позиции для items с меньшим объёмом исторических данных. В краткосрочной перспективе это может заменить item с высоким прогнозом клика на item, о котором модель знает меньше.

Онлайн-результат очевиден:

ΔCTR < 0

Но целевой результат — не «больше кликов на этом показе». Целевой результат — каталог, который остаётся доступным для discovery и со временем даёт пользователям больше причин возвращаться.

Если retention измеряется позже, на другой когорте или вообще не связан с ranking-экспериментом, то в решение о rollout попадает только одна сторона компромисса. CTR — это измеренная стоимость. Retention — неизмеренное обещание.

Решение не в том, чтобы требовать от diversity выигрыша у popularity по немедленному CTR. Нужно явно решить, стоит ли discovery в long tail краткосрочной стоимости для ranking, а затем измерить ответ на этом горизонте.
