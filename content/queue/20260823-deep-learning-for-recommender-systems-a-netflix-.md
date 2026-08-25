---
id: 20260823-4dae1aed
slug: deep-learning-for-recommender-systems-a-netflix-
pillar: recsys_101
status: skipped
created: 2026-08-23T11:55:45+00:00
idea: Explain one non-obvious point from: Deep learning for recommender systems_ A Netflix case study
source_url: course_notes.md :: Deep learning for recommender systems_ A Netflix case study
variant: 
tg_message_id: 72
rewrite_note: 
post_urn: 
published_at: 
material_ref: course_notes.md :: Deep learning for recommender systems_ A Netflix case study
skip_reason: no answer within 44h
---

<!-- variant_a -->
30%: that was the reported improvement from representing time continuously rather than as discrete buckets in the case-study material.

That comparison is more useful than it first appears. A recommender can receive time as “day” or “week.” Those encodings create hard borders: an interaction just before a weekly boundary and one just after it land in different categories, although the elapsed time between them may be small.

A continuous representation gives the model a different signal. Elapsed time can vary without being forced into a calendar bin. The model can learn the relationship between time and the target from the data, rather than inheriting boundaries chosen by the feature engineer.

This is not evidence that continuous time beats discrete time for every model or objective. The reported 30% is relative to a discrete-time feature representation in this case-study material, not a universal result.

But day and week buckets should be a baseline encoding, not an automatic default. If time matters to the task, ablate its representation before spending the next iteration on a new model family.

The representation of time deserves an ablation before the model family does.

<!-- variant_b -->
Calendar buckets are not a neutral representation of time. They impose discontinuities that the user never created.

Consider two interactions around a weekly boundary. One happens late on Sunday; another happens shortly after Monday begins. With week-level buckets, they become different categorical values, even when very little time passed between them.

That is a feature-engineering decision, not a property of user behavior.

A continuous time feature avoids that forced jump. Instead of telling the model which calendar bin an event belongs to, it can provide elapsed time as a value. The model can then learn whether timing is useful for the target and how that signal changes.

In the case-study material, continuous time was reported to improve results by 30% over a discrete representation. That result is relative to the time-feature encoding used there; it does not establish that continuous time wins across every recommender or objective.

I would treat day and week buckets as a baseline encoding, not the default production feature. When time is available, the first experiment should compare the representation—not only the model architecture.

<!-- ru_a -->
30%: именно такое улучшение было заявлено при представлении времени как непрерывной величины, а не как набора дискретных интервалов, в материалах кейса.

Это сравнение полезнее, чем может показаться на первый взгляд. Рекомендательная система может получать время в виде «дня» или «недели». Такие кодировки создают жёсткие границы: взаимодействие непосредственно перед границей недели и взаимодействие сразу после неё попадают в разные категории, хотя прошедшее между ними время может быть небольшим.

Непрерывное представление даёт модели другой сигнал. Прошедшее время может меняться без принудительного попадания в календарный интервал. Модель может выучить связь между временем и target по данным, а не наследовать границы, выбранные разработчиком признаков.

Это не доказывает, что непрерывное представление времени лучше дискретного для любой модели или objective. Заявленные 30% относятся к представлению признака времени через дискретные интервалы в материалах этого кейса, а не являются универсальным результатом.

Но интервалы «день» и «неделя» должны быть baseline-кодировкой, а не автоматическим default. Если время важно для задачи, проведите ablation его представления, прежде чем тратить следующую итерацию на новое семейство моделей.

Представление времени заслуживает ablation раньше, чем семейство моделей.

<!-- ru_b -->
Календарные бакеты — не нейтральное представление времени. Они создают разрывы, которых пользователь никогда не формировал.

Рассмотрим два взаимодействия по разные стороны границы недели. Одно происходит поздно в воскресенье, другое — вскоре после начала понедельника. При разбиении по неделям они становятся разными категориальными значениями, даже если между ними прошло совсем немного времени.

Это решение по feature engineering, а не свойство поведения пользователей.

Непрерывный временной признак позволяет избежать этого принудительного скачка. Вместо того чтобы сообщать модели, к какому календарному бакету относится событие, можно передать прошедшее время как значение. Тогда модель сможет сама выучить, полезен ли момент времени для целевой переменной и как меняется этот сигнал.

В материалах кейса сообщается, что непрерывное время улучшило результаты на 30% по сравнению с дискретным представлением. Этот результат относится к способу кодирования временного признака, использованному в том кейсе; он не доказывает, что непрерывное время выигрывает в любой рекомендательной системе или для любой целевой функции.

Я бы рассматривал разбиение по дням и неделям как baseline-кодирование, а не как production feature по умолчанию. Если время доступно, первый эксперимент должен сравнивать именно представление, а не только архитектуру модели.
