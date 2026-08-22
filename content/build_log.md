# Build log notes (raw input for pillar 6)

What you are building right now, in enough detail that a post can be written from it
without inventing anything. One `##` section per project or decision.

Format:

## <project or decision> — <YYYY-MM>
- goal:
- the decision and the alternative you rejected:
- what actually happened:
- numbers (latency, cost, accuracy, time saved):

---

## brand-engine — 2026-08
- goal: publish a LinkedIn post every two days with ~30 seconds of manual effort per post
- the decision and the alternative you rejected: approval and publishing were split into
  two scheduled jobs instead of publishing straight from the approval tap. LinkedIn's API
  has no scheduled publishing, so the posting slot has to be ours anyway - and once it is,
  a 20-minute polling lag on approvals costs nothing and removes the need for a webhook
  server entirely
- what actually happened: the pipeline runs on GitHub Actions with no hosted service; the
  approval surface is a Telegram inline keyboard; a critic pass scores every draft against
  a rubric before it is ever shown
- numbers: ~$0.03-0.05 of model spend per post, 6 scheduled workflows, 0 servers
