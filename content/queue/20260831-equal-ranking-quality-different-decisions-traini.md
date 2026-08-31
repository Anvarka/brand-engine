---
id: 20260831-cdf9c37f
slug: equal-ranking-quality-different-decisions-traini
pillar: paper_teardown
status: pending
created: 2026-08-31T11:33:29+00:00
idea: A reranker can win nDCG while producing materially different thresholded decisions, so production evaluation must measure retained-set stability and downstream decisions—not ranking quality alone—especially when scores depend on document order.  Why now: A fresh result exposes a failure mode in LLM rerankers that becomes more consequential as scores drive filtering, answer generation, and preference selection.
source_url: https://arxiv.org/abs/2608.26762v1
variant: 
tg_message_id: 94
rewrite_note: 
post_urn: 
published_at: 
material_ref: https://arxiv.org/abs/2608.26762v1
---

<!-- variant_a -->
Five trained scorers were within 0.010 nDCG@10 on passage reranking, yet their thresholded retained sets overlapped by only 0.66–0.84 after reordering the same candidates.

That gap matters whenever a reranker score is more than a display order.

LLM rerankers, reward models, and multi-document QA scorers often evaluate several candidates in one prompt. A document’s score can therefore depend on where it appears relative to the others. nDCG can stay nearly unchanged because the ranking remains broadly correct, while scores move across the threshold that decides what is retained.

The paper’s comparison makes this uncomfortable: a published reranker achieved the highest retained-set F1 in the comparison, but its retained-set overlap was still only 0.667.

Prompt-time interventions tested by the authors did not remove the order dependence.

I would not ship a thresholded reranker based on nDCG alone. Evaluate it under candidate permutations, report retained-set overlap, and measure agreement in the downstream decision: which passages reach generation, which responses are selected, or which items survive filtering.

<!-- variant_b -->
A reranker can be equally good at ranking and still make a different production decision.

That sounds contradictory only if nDCG is treated as a decision metric. It is not. nDCG measures whether relevant items are ordered well; it does not guarantee that the same items cross a score threshold.

A recent study shows why this becomes acute with LLM scorers. Rerankers, reward models, and multi-document QA scorers can score several candidates in one prompt, making each score conditional on candidate order.

On passage reranking, five trained scorers within 0.010 nDCG@10 retained sets with only 0.66–0.84 overlap when the candidates were reordered. A published reranker with the best retained-set F1 in the comparison still had overlap of 0.667.

This is not a cosmetic instability. A threshold may determine which evidence reaches an answer generator, which response a preference model selects, or which candidates enter the next stage.

My position: if scores trigger a discrete action, retained-set stability and downstream-decision agreement belong next to nDCG in the release gate.

<!-- ru_a -->
Пять обученных скореров показали разницу не более 0,010 по nDCG@10 на задаче reranking passages, однако после перестановки одних и тех же кандидатов их множества, оставленные после применения порога, пересекались лишь на 0,66–0,84.

Этот разрыв важен всякий раз, когда score reranker определяет не только порядок отображения.

LLM-rerankers, reward models и скореры для multi-document QA часто оценивают несколько кандидатов в одном промпте. Поэтому score документа может зависеть от того, где именно он расположен относительно остальных. nDCG может почти не измениться, поскольку ranking в целом остаётся корректным, но scores пересекают порог, который определяет, что будет оставлено.

Сравнение в статье заставляет почувствовать себя неуютно: опубликованный reranker показал самый высокий F1 для множества оставленных кандидатов, но overlap этого множества всё равно составил лишь 0,667.

Протестированные авторами вмешательства на этапе подготовки промпта не устранили зависимость от порядка.

Я бы не выпускал в прод reranker с порогом, ориентируясь только на nDCG. Оценивайте его на перестановках кандидатов, сообщайте overlap множеств оставленных кандидатов и измеряйте согласованность в downstream-решении: какие passages доходят до генерации, какие ответы выбираются или какие items проходят фильтрацию.

<!-- ru_b -->
Reranker может одинаково хорошо ранжировать кандидатов и при этом принимать другое production-решение.

Это звучит противоречиво только если считать nDCG метрикой принятия решений. Это не так. nDCG измеряет, насколько хорошо упорядочены релевантные элементы; он не гарантирует, что те же элементы пересекут score threshold.

Недавнее исследование показывает, почему с LLM-скорами проблема становится особенно острой. Reranker’ы, reward models и scorers для multi-document QA могут оценивать несколько кандидатов в одном prompt, из-за чего каждый score зависит от порядка кандидатов.

В задаче passage reranking пять обученных scorers с разницей не более 0.010 по nDCG@10 сохраняли множества с пересечением всего 0.66–0.84 при изменении порядка кандидатов. У опубликованного reranker’а с лучшим retained-set F1 в этом сравнении пересечение всё равно составляло 0.667.

Это не косметическая нестабильность. Threshold может определять, какие evidence попадут к генератору ответа, какой response выберет preference model или какие кандидаты перейдут на следующий этап.

Моя позиция: если scores запускают дискретное действие, то стабильность retained set и согласованность downstream-решений должны стоять рядом с nDCG в release gate.
