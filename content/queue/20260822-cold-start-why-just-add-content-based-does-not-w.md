---
id: 20260822-469e88c3
slug: cold-start-why-just-add-content-based-does-not-w
pillar: recsys_101
status: pending
created: 2026-08-22T21:12:06+00:00
idea: Content-based features solve item cold start only where the catalog metadata is as discriminative as behaviour - which is almost never.  Why now:
source_url: local://seed/3e8563e330d9
variant: 
tg_message_id: 64
rewrite_note: 
post_urn: 
published_at: 
material_ref: local://seed/3e8563e330d9
---

<!-- variant_a -->
At zero interactions, a content model can score a new item. That is its real cold-start advantage—not proof that it can recommend the item well.

In Lecture 4, I cover DSSM-style models that map user/query and item signals into vectors, then rank with a dot product or cosine similarity. An item can receive a representation before it collects clicks, shows, or ratings.

The hidden assumption is that catalog metadata separates items as well as user behaviour does.

Usually, it does not.

Metadata can describe what an item is. Interaction data describes which users chose it over alternatives. Those are not interchangeable signals. Two items may look nearly identical in text or category features while attracting very different audiences.

So content features solve an availability problem: a new item can enter retrieval or ranking before it has history.

They do not automatically solve preference estimation. Adding an item embedding built from metadata does not create the behavioural distinctions missing from the interaction matrix.

My rule of thumb: use content to give new items an initial representation, then let behaviour determine whether that representation is actually discriminative enough for ranking.

Do you measure cold-start coverage separately from cold-start ranking quality?

<!-- variant_b -->
Content-based recommendation is often a catalog-coverage fix disguised as a ranking fix.

The usual cold-start plan is straightforward: a new item has no clicks or ratings, so encode its text, category, or other available metadata and rank it against a user representation.

That is a valid first step. In Lecture 4, DSSM is one way to do it: represent the query/user and document/item as vectors, then use dot product or cosine similarity for ranking.

But the model can only distinguish what the features distinguish.

If the catalog says two items are similar, their content representations will tend to be similar. Behaviour may later show that they serve different users, compete in different contexts, or receive very different choices. Those distinctions are absent when an item is new.

This is why “just add content-based” underdelivers. It gives the system a way to score every item. It does not guarantee that the score contains the preference signal collaborative data would have supplied.

I would treat metadata as a bridge across the first interactions, not as a replacement for them. The key question is whether catalog features are discriminative enough for the decision you need to make.
