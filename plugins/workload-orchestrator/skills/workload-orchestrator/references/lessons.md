# Lessons from running it

These came out of six real rounds and the retrospective the human asked for. Each one is a
thing that went wrong, then the fix.

## Coordination

- **Several artifacts confused the human.** A decision inbox, a stopping-point page and a
  planner, each with part of the picture, meant the human couldn't find the decisions. Fix:
  one app with tabs (Decide / Now / Next / Later). When you replace a page, put a "moved"
  banner on the old one and migrate its open items. Don't delete it.
- **A note-only answer disappeared.** The human answered with a note and no option, the item
  moved to "Sent" and they lost sight of it. Fix: act on notes like answers, and reply saying
  what you did with the note.
- **Kanban columns didn't fit.** The human wanted horizons (Now / Next / Later, Shape-Up
  style), not workflow states. Workflow state is a chip on the card (`status`).
- **"Fits into one sitting", fleet caps and other jargon weren't understood.** Fix: say
  "3 workers, about 2 hours" instead of the jargon.
- **Recommendations need a label.** Cards' recommendations read as facts until they were
  labelled "Claude recommends:".
- **The human wants dependencies and parallelism made visible.** That's what the page's
  worker plan and "Check before starting" warnings are for. It also wants a progress bar with
  hours and done-by times.

## Merging

- **Don't gate your own merges on the human.** If the rules say you merge on evidence, merge.
  Waiting for a thumbs-up stalls the round.
- **Verify before you publish a claim.** One card said a ticket was "blocked by the vendor"
  when it could be built against a stand-in. Check the issue body and the code, not memory.
- **Pin merges to the commit SHA.** `git merge-tree --write-tree` prints a tree id. Passing
  it as `expectedHeadSha` gives a confusing 409. Use `git rev-parse pr/N`.
- **Crossed messages.** A worker pushed to a PR that had just merged. Another worker's PR
  conflicted with a fresh merge. Fix: after every merge, tell running workers to merge main.
  Workers merge main in and never rebase.
- **Workers find what the brief missed.** One example: retrying a transaction didn't fix stale
  connections until the pool was also reset. Trust the evidence on the results page, not the
  brief. File the worker's deferred items right away, as issues plus cards, so nothing lives
  only in chat.

## Workers

- **Results pages, not QA pages.** A spike's page should show what was learned. A fix's page
  should show the scenarios. Either way, proof for every claim.
- **Environment quirks cost hours.** Registry rate limits, browser binary versions, daemon
  timeouts. Each one fixed once goes into the worker prompt base for the next round.
- **CI may be unavailable.** If there's no CI compute, the worker's own full-suite run (on its
  branch merged with main) plus the results page is the gate. A separate verifier session
  was tried and stopped at the human's request: it doubled the cost and found nothing the
  results pages didn't show.

## Talking to the human

- They're on mobile all the time. Short messages, the action first, links over pasted
  content.
- Message them as soon as a question lands. Don't batch questions until the end of a round.
- State the cost before starting workers. A card moved into Now is the go-ahead.
