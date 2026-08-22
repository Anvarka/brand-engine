# Content pillars

Rotation order is the list below; `data/state.json:pillar_cursor` points at the next one.
Phase 3 replaces round-robin with an ε-greedy pick over measured engagement.

Every pillar entry defines: what the post is, where material comes from, and the specific
failure mode to avoid for that format.

---

## 1. paper_teardown
**What:** one recent paper, one takeaway that changes what you would do in production.
**Source:** arXiv cs.IR / cs.LG harvest.
**Shape:** what the paper claims → the one detail that matters → what it means for a real
system → where it will not hold.
**Avoid:** summarizing the abstract. If the post could be written after reading only the
title, it is worthless. Always include the caveat the authors downplay.

## 2. recsys_101
**What:** one concept from the course, explained standalone in 1200 characters.
**Source:** `online_course_resSys/recSys_course/Lecture *.pptx`, seminars, HW notebooks.
**Shape:** the naive expectation → why it breaks → the actual mechanism → a rule of thumb.
**Avoid:** textbook tone and completeness. One concept, one insight, stop.
**CTA:** may point to the course, at most once every three posts of this pillar.

## 3. war_story
**What:** something that broke in production and what it cost.
**Source:** author's notes in `content/war_stories.md` (fill this file as things happen).
**Shape:** the symptom → the wrong hypothesis → the actual cause → what changed afterwards.
**Avoid:** heroics and vagueness. Names of employers and unverified numbers stay out unless
they are in the notes verbatim. This is the highest-value pillar for inbound offers — it is
the only proof that the author has actually operated a system.

## 4. industry_teardown
**What:** how a known company actually does it, read from their own engineering material.
**Source:** Netflix / Spotify Research / Pinterest / Airbnb / DoorDash / Uber / Meta AI
engineering blogs; `recSys_course/x-algorithm` sources; Netflix DL case study deck.
**Shape:** their constraint → their choice → the part that only works at their scale →
what a 10-engineer team should copy instead.
**Avoid:** cargo-culting. The interesting half is always what does *not* transfer.

## 5. hot_take
**What:** an argued position that a competent reader could disagree with.
**Source:** none — this is opinion, backed by arithmetic.
**Shape:** the common belief → why it is wrong or overstated → the numbers → the condition
under which the common belief is actually right.
**Avoid:** contrarianism for its own sake, and takes about topics outside recsys/ML infra.
Must contain at least one quantitative argument.

## 6. build_log
**What:** what the author is building right now, with real detail.
**Source:** own repositories — `brand-engine` itself, `speculative_decoding_ma`, `dlbot`,
`finpulse`, `kalman_filter_with_kitti`.
**Shape:** the goal → the design decision and its alternative → what actually happened →
the number that came out.
**Avoid:** announcement tone. Show a decision, not a milestone.

## 7. career_meta
**What:** how to prepare for or think about ML/RecSys work — interviews, system design,
skill choices. **Cap: one per month.**
**Avoid:** generic career advice. Must be specific to recsys or ML infrastructure.
