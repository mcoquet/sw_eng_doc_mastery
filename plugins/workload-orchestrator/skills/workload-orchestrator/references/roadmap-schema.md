# Roadmap artifact: capabilities, data and writes

`assets/roadmap.html` is a single-page app. It renders entirely from its artifact database
and live-updates through `onSnapshot`. You write the plan with `ArtifactData`. The human
moves cards and answers decisions in the page. **Send** posts one comment to you
(`comments.sendToClaude`), and that comment wakes your session.

## Publishing

Load the `artifact-design` / `artifact-capabilities` skills as the Artifact tool requires.
Set `__PROJECT__` and `__REPO__` in the file, then publish with:

```json
{
  "db": {"rules": [
    {"path": "cards",     "read": "view", "write": "admin"},
    {"path": "meta",      "read": "view", "write": "admin"},
    {"path": "items",     "read": "view", "write": "admin"},
    {"path": "placement", "read": "view", "write": "interact"},
    {"path": "answers",   "read": "view", "write": "interact"}
  ]},
  "user": {},
  "comments": {}
}
```

The rules split the data between the two sides:
- **You (admin) own** `cards`, `meta` and `items`.
- **The human writes** `placement` and `answers`.

So the page never overwrites your text, and you never overwrite their moves.

On a redeploy, omit `capabilities` to keep them. Publish to the same `file_path` (or the
artifact's `url` from another conversation) so the link stays the same.

## Collections

### `cards/<id>`: one per ticket or ticket group (you write)

| field | type | notes |
|---|---|---|
| `n` | number[] | issue numbers; the label shows `#n` |
| `title` | string | plain words, the user-visible problem |
| `problem` | string | what's wrong / what gets built |
| `why` | string | why it matters to users, one or two sentences |
| `importance` | `critical`/`high`/`medium`/`low` | sorts within a column |
| `effort` | `S`/`M`/`L` | |
| `hours` | number | worker-hours; drives the worker plan and the pipeline bar |
| `effortNote` | string | what the hours include |
| `deadline` | `deploy`, `none`, or any tag (shows as "before <tag>"; add labels in the `DEADLINE` map) | shown as a chip |
| `areas` | string[] | code regions; shared areas mean same worker |
| `blockedBy`, `blocks` | card ids | workerPlan waits on unmerged `blockedBy` |
| `decisions` | number | open questions count |
| `decisionsNote` | string | |
| `rec` | string | shown as "Claude recommends:" |
| `status` | `idle`/`running`/`pr`/`waiting`/`merged` | merged cards drop out of the columns |
| `pr` | number | |
| `results` | https URL | the worker's results page |
| `col`, `order` | | **default** placement only, used until the human moves it |

### `placement/<card id>`: `{col: "now"|"next"|"later", order: number, at: iso}`

This is where the card really sits. The human writes it by moving cards. You write it only:
- when you're adding a card;
- when you promote a card from Next to Now (see "Pulling from Next" in SKILL.md);
- when the human asked you to move something.

Never move a card out of Later, and never reorder Next: both are the human's calls.

### `meta/plan`: `{next: [{id, why}], recNote}` (you write)

Your recommended order for Next. The page offers a "Use this order" button for it.

### `items/<id>`: decisions for the Decide tab (you write)

```json
{
  "title": "Keep source UIDs or replace them?",
  "context": "Plain-language background. What happens with each choice.",
  "options": [{"id": "a", "label": "Keep them", "detail": "…"}, {"id": "b", "label": "…"}],
  "recommend": "a",
  "priority": "now" | "soon" | "later",
  "card": "c55",
  "links": [{"label": "PR #158", "url": "https://…"}],
  "createdAt": "iso",
  "status": "open" | "done",
  "resolution": "What was decided and done (shown under Decided)",
  "doneAt": "iso"
}
```

Put the default and the deadline in `context`, for example: "If no answer by 09:00 UTC I go
with A."

### `answers/<item id>`: `{choice, note, at}` (the human writes)

An item with an answer moves to "Sent, Claude is on it". Once you've acted on it, set the
item's `status: "done"` and a `resolution`. Leave the answer doc alone.

## Writing

- **Batch.** Use `ArtifactData` `batch` with up to 50 entries. `file_path` entries keep big
  seeds out of the conversation.
- **Versions.** Writing to an existing doc needs `if_version` (the `version` you last read).
  Creating a doc doesn't. A version conflict means the human changed it: re-read, then redo.
- **Field placement.** In a batch entry, every field except `op`, `collection`, `doc_id`,
  `data`/`file_path` and `if_version` must go inside `data`.
- **Markup.** The page escapes all text. Links render only if they start with `https://`.

## Reading what the human did

When a "Roadmap update" comment wakes you, its text summarises the moves and answers. Still
read them from the db before acting:
- query `placement` where `col in [now, next]`;
- list `answers` and diff them against open `items`.

## The "done this round" count

The pipeline bar counts merged cards whose placement is `now`. To start a new round's count
from zero, set those merged cards' placement to `later`. Merged cards stay hidden either way.
