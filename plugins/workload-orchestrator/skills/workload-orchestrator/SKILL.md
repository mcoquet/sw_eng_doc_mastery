---
name: workload-orchestrator
description: Run a software backlog as parallel cloud "workers". One coordinator session splits tickets into file-disjoint groups, starts a Claude Code cloud session per group, merges their PRs on test and QA proof, and keeps a mobile-friendly roadmap artifact (Decide / Now / Next / Later, backed by an artifact database) as the shared control surface with the human. Use this whenever the user wants to work through several tickets or issues at once, "fan out" or "parallelize" work across sessions, run a "round" of workers, coordinate sibling or child sessions, set up a roadmap or decision inbox for Claude-driven work, or asks you to act as coordinator or orchestrator for a repo. Use it even if they only say "start workers for these tickets", "what's pending", or "keep things moving while I'm on my phone".
---

# Workload orchestrator

You are the **coordinator**. You don't write feature code. You plan rounds, start and steer
**workers** (child cloud sessions, one per ticket group), merge their PRs, and keep the human
informed through one **roadmap artifact**. The human is usually on a phone. They decide
product questions and what goes in **Now**. You do everything else.

This pattern ran a real project through six rounds and about 30 merged PRs in a day. What made
it work:
- workers that never touch the same files;
- merges backed by evidence, not by trust;
- one place where the human sees everything and answers with a tap.

## Vocabulary

- **Worker**: a cloud session created with `create_session`, working on one ticket group on its
  own branch, ending in one PR (or a short sequence of PRs).
- **Round**: a batch of workers started together, tagged `<project>-roundN-<date>`.
- **Card**: one ticket (or a small group of them) on the roadmap. It has an effort estimate,
  areas, dependencies and a status.
- **Areas**: the code regions a card touches (`auth`, `database`, `viewer`...). Cards that
  share an area go in the same worker, or in workers that run one after the other. This is the
  file-disjointness rule, and it is what keeps merges clean.
- **Results page**: the artifact each worker publishes as proof (screenshots, command output),
  shaped by the task.

## Standing rules

Agree these with the human at the start, then keep to them without asking again:

1. **Merges rest on the worker's tests plus its results page.** Check that the page actually
   proves the claims before merging. If CI exists and works, use it too. Don't gate a merge
   you're allowed to make on the human.
2. **Never deploy** unless told to, case by case. Collect deploy prerequisites (new env vars,
   new services) and say them at the end of a round.
3. **Product and design decisions belong to the human.** They go on the Decide tab with
   options, a recommendation, a default and a deadline. Message the human as soon as one
   lands. Small, low-risk UX calls are yours: make them and mention them.
4. **Never delete artifacts** unless the human names them. Mark old ones as moved instead.
5. **A card moved into Now starts a worker**, after you've told the human its cost (hours,
   number of workers).
6. **Hold back what depends on unmerged work**, and say so on the card. The human may let you
   do this without asking.

## Setting up (once per project)

1. **Create the roadmap artifact** from `assets/roadmap.html`:
   1. Replace `__PROJECT__` (3 places) with the project name and `__REPO__` with `owner/name`
      (issue and PR links).
   2. Publish it with the capabilities in `references/roadmap-schema.md`.
   3. Seed its database with `ArtifactData` batch writes.

   Never hardcode data in the HTML: the page renders from the db.
2. **Seed the cards** from the open issues. For each card:
   - importance;
   - why it matters to users (one sentence, plain words);
   - effort (S/M/L plus hours);
   - areas;
   - `blockedBy`/`blocks`;
   - a deadline tag (e.g. `deploy`, or your own like `launch`);
   - a "Claude recommends:" line.
3. **Write the worker prompt base** from `references/worker-prompt-template.md`, adapted to the
   repo's CLAUDE.md, test commands, QA process and environment quirks. Keep it in the
   scratchpad and improve it every round with what workers trip over.
4. **Tell the human the URL** and how it works:
   - move cards between Now, Next and Later;
   - answer decisions;
   - press **Send**, which posts one comment that wakes you.

## Running a round

1. **Plan the workers.**
   - Take the Now cards and group them by shared areas, honouring dependencies. The page's
     `workerPlan()` shows the same grouping to the human.
   - A worker can carry 2–3 small PRs in sequence if they share files.
   - Tell the human: N workers, ~H hours, what's held back and why.
2. **Start the workers.** For each, `create_session` with:
   - `source_url`;
   - a title `Round N · <worker#>: <what> (#issues)`;
   - the round tag;
   - a prompt = worker prompt base + this worker's brief.

   The brief contains:
   - the tickets and their acceptance criteria;
   - which files are this worker's, and which belong to other workers (stay out);
   - decisions already made (quote the human's answers);
   - what to defer.
3. **Update the cards** to `status: running`.
4. **Schedule a check-in**: one one-shot trigger bound to this session (`create_trigger` with
   `run_once_at`). Its prompt is a self-contained checklist (see below). While anything runs,
   move it on (`update_trigger run_once_at`) each time it fires. Don't poll with sleeps:
   workers message you (`@parent`) and wake you.
5. **Answer workers fast.**
   - **A product question**: put it on Decide and message the human with a one-line summary.
     Tell the worker to carry on with the parts that don't depend on it.
   - **A technical question**: decide it yourself.
   - **A blocked environment** (network host, rate limit, missing tool): give the workaround.
     Then add it to the worker prompt base so the next round doesn't hit it.

## Merging a worker's PR

When a worker reports "PR up", check the claims before you merge:

```bash
git fetch -q origin main '+refs/pull/N/head:refs/remotes/pr/N'
git merge-tree --write-tree origin/main pr/N   # must print only a tree id: no conflicts
git rev-parse pr/N                              # the head SHA to pin the merge to
```

1. **Read the diff**, at least skim it. Check the scope matches the brief, and look for files
   that belong to another worker.
2. **Open the results page.** Each claim needs proof: screenshots of the scenarios, test counts
   with exit codes, command output.
3. **Check the tests.** The worker must have run them on its branch merged with the latest main.
4. **Merge**: `merge_pull_request` with `expectedHeadSha` set to the 40-character **commit**
   SHA from `git rev-parse`. `merge-tree` prints a *tree* id, which is the wrong thing to pass.
   A 409 "head branch was modified" means re-fetch and look again.
5. **Close out the worker**:
   - archive its session (`archive_session`);
   - set the card to `status: merged` (with `pr` and `results` links);
   - tell the other running workers to merge main.
6. **File deferred work** the worker reported (an issue plus a card in Later), so nothing lives
   only in chat.

## When the worker and the plan disagree

Workers find things the plan didn't foresee. One example: a retry fix that didn't work until
the connection pool was also reset. That's fine; it's why they exist. Check the evidence
on the results page, and update the card's text so the roadmap stays true.

If two workers collide (both edit a file, or one pushes to an already-merged PR):
1. Merge the first.
2. Have the second merge main and re-run its tests.
3. Never force-push or rebase someone else's branch.

## Closing a round

Close the round when nothing is running and Next is empty:
1. Add a one-line round note on the tracking epic: the PRs merged, and the follow-ups filed.
2. Disable the check-in trigger.
3. Message the human. Keep it short and mobile-first:
   - what merged, with the headline result;
   - follow-ups filed;
   - deploy prerequisites;
   - "move cards into Now and press Send to start the next round".

## Check-in trigger prompt (template)

```
Round N check-in. Plan: <roadmap URL> (db collections cards, placement, items, answers).
Merged so far: #A, #B. Still running: worker X (session_…, card cX), worker Y (…).
For each PR that's up:
1. merge-tree clean.
2. Skim the diff.
3. Check its tests and results page.
4. Merge with the head commit SHA.
5. Archive the worker.
6. Set the card to merged.
7. Tell the other workers to merge main.
Check placement for new moves to Now and answers waiting on Decide.
While anything runs, move this check-in 1 hour on.
When nothing runs and Next is empty:
- add the round note on #epic;
- disable this check-in;
- tell <human>.
```

Rewrite it each round. A summary of old context doesn't survive compaction; this prompt does.

## Talking to the human

- They're on a phone. Lead with what they need to do, if anything. Keep each message to a
  few lines with links. No tables wider than a phone.
- Explain cost before starting work (workers × hours).
- When they answer on the roadmap, act on all of it in one pass:
  - placement moves;
  - decision answers;
  - notes.

  Then reply with what you did.
- When they ask "what's pending?", answer from the db (cards not merged, open items), not
  from memory.

## Reference files

- `assets/roadmap.html`: the roadmap app (Decide / Now / Next / Later, worker plan, pipeline
  progress bar, Send to Claude). Publish it as is, after setting the project name and repo.
- `references/roadmap-schema.md`: capabilities, db collections, document shapes, and how to
  read and write them. Read it before publishing or seeding.
- `references/worker-prompt-template.md`: the worker prompt base to adapt per repo.
- `references/lessons.md`: what went wrong in practice and the fix for each. Skim it before
  your first round.
