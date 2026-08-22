---
id: 20260822-469e88c3
slug: cold-start-why-just-add-content-based-does-not-w
pillar: recsys_101
status: published
created: 2026-08-22T21:12:06+00:00
idea: Content-based features solve item cold start only where the catalog metadata is as discriminative as behaviour - which is almost never.  Why now:
source_url: local://seed/3e8563e330d9
variant: a
tg_message_id: 67
rewrite_note: Drop the reference to 'Lecture 4' entirely - the reader cannot resolve it. Explain the idea on its own authority.
post_urn: urn:li:share:7497061869258502144
published_at: 2026-08-22T22:47:18+00:00
material_ref: local://seed/3e8563e330d9
approved_at: 2026-08-22T22:15:39+00:00
---

<!-- variant_a -->
Two new items can carry the same catalog metadata and still belong in very different recommendation lists. Before users interact with them, a content model cannot distinguish those audiences.

That is the limit of content-based cold start.

At retrieval time, metadata can make a new item eligible beside items with similar fields. This is useful: a new item has no interaction history, so it needs some basis for entering a candidate set.

But repeated or coarse metadata creates a specific failure mode. Several items are treated as near-substitutes because the catalog describes them similarly, while users later reveal that they attract different audiences. The content signal gives them the same first placement; behaviour separates them only after impressions, clicks, saves, or other interactions accumulate.

The practical check is temporal. Compare an item’s metadata-derived neighbours at launch with its interaction-derived neighbours once it has history. If the later neighbours diverge, metadata was not identifying the audience. It was only providing a prior for where to start.

Content features earn a new item its first candidates. Behaviour determines whether those candidates were actually the right ones.

<!-- variant_b -->
Metadata is a cold-start prior, not a replacement for behavioural identification.

The mistake is to call item cold start “solved” because every new catalog item has content features. A feature vector is enough to place an item somewhere before it has interactions. It is not necessarily enough to determine who should see it.

The failure appears at retrieval. When multiple new items have repeated or coarse metadata, they become eligible for similar candidate sets. A content-only system has little reason to separate them further: the available evidence says they are alike.

Later interaction data can contradict that first grouping. Users may consistently engage with one item alongside a different set of items than the metadata suggested. The initial content neighbours and the later behavioural neighbours are then telling different stories.

A useful evaluation is to compare those two neighbourhoods over time: metadata-similar items when the item is new, interaction-derived neighbours after it matures. Large disagreement means the catalog supplied a starting position, not an audience identity.

Content-based features are essential for the first exposure. They should not be mistaken for the signal that resolves item-level relevance.

<!-- ru_a -->
Два новых айтема могут иметь одинаковые метаданные каталога и при этом подходить для совершенно разных recommendation lists. Пока пользователи с ними не взаимодействовали, content model не может различить эти аудитории.

В этом и заключается ограничение content-based cold start.

На этапе retrieval метаданные могут сделать новый айтем кандидатом наряду с айтемами, у которых похожие поля. Это полезно: у нового айтема нет истории взаимодействий, поэтому ему нужна какая-то основа, чтобы попасть в candidate set.

Но повторяющиеся или слишком общие метаданные создают особый failure mode. Несколько айтемов воспринимаются как почти взаимозаменяемые, потому что каталог описывает их схожим образом, тогда как позже пользователи показывают, что эти айтемы привлекают разные аудитории. Content signal даёт им одинаковое первоначальное размещение; поведение разделяет их только после того, как накапливаются показы, клики, сохранения и другие взаимодействия.

Практическая проверка — временная. Сравните соседей айтема, полученных из его метаданных при запуске, с соседями, определёнными на основе взаимодействий после накопления истории. Если позже эти соседи расходятся, значит, метаданные не определяли аудиторию. Они лишь задавали prior для начальной точки.

Content features дают новому айтему его первых кандидатов. Поведение определяет, действительно ли эти кандидаты были подходящими.

<!-- ru_b -->
Метаданные — это prior для cold start, а не замена поведенческой идентификации.

Ошибка — считать cold start для объектов каталога «решённым» только потому, что у каждого нового объекта есть контентные признаки. Вектора признаков достаточно, чтобы определить объекту какое-то место ещё до появления взаимодействий. Но этого не обязательно достаточно, чтобы понять, кому его следует показывать.

Проблема проявляется на этапе retrieval. Когда у нескольких новых объектов метаданные повторяются или заданы слишком грубо, они попадают в похожие candidate set. У системы, которая опирается только на контент, мало оснований дополнительно их разделять: доступные данные говорят, что они похожи.

Позднее данные о взаимодействиях могут опровергнуть это первоначальное группирование. Пользователи могут стабильно взаимодействовать с одним объектом вместе с другим набором объектов, не тем, который предполагали метаданные. Тогда исходные контентные соседи и последующие поведенческие соседи рассказывают разные истории.

Полезно со временем сравнивать эти два соседства: объекты, похожие по метаданным, когда объект новый, и соседей, полученных из взаимодействий, после того как у объекта накопилась история. Сильное расхождение означает, что каталог задал стартовую позицию, но не определил аудиторию объекта.

Контентные признаки необходимы для первого показа. Но не следует принимать их за сигнал, который определяет релевантность на уровне объекта.

<!-- chosen -->
Two new items can carry the same catalog metadata and still belong in very different recommendation lists. Before users interact with them, a content model cannot distinguish those audiences.

That is the limit of content-based cold start.

At retrieval time, metadata can make a new item eligible beside items with similar fields. This is useful: a new item has no interaction history, so it needs some basis for entering a candidate set.

But repeated or coarse metadata creates a specific failure mode. Several items are treated as near-substitutes because the catalog describes them similarly, while users later reveal that they attract different audiences. The content signal gives them the same first placement; behaviour separates them only after impressions, clicks, saves, or other interactions accumulate.

The practical check is temporal. Compare an item’s metadata-derived neighbours at launch with its interaction-derived neighbours once it has history. If the later neighbours diverge, metadata was not identifying the audience. It was only providing a prior for where to start.

Content features earn a new item its first candidates. Behaviour determines whether those candidates were actually the right ones.
