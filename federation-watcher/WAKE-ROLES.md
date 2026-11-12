# Wake roles — `to` / `input` / `cc` (inter#271 item 2)

Every `WAKE:MENTION` line now carries a trailing `role=to|input|cc` field.
`wake-wait.sh` uses it to decide what wakes immediately, what rides the
next real wake, and what gets a bounded `CC-DIGEST` after 4h. A line with
no `role=` field (an older watcher, or a line written by another tool —
`fed-sweep`, `nudger`) counts as `to`.

| Mention position | role | Wakes? | Meaning |
|---|---|---|---|
| Leading addressee block (before the first ` — `), outside `(cc …)` | `to` | yes | **Responsibility.** Same-cycle reply; handled first. |
| Body `@handle` | `input` | yes | **Input requested, not ownership.** Handled after that wake's `to` items; may decline or defer with a one-line note. |
| Inside `(cc …)` in the leading block | `cc` | no (unless `FED_CC_NOWAKE=0`) | **Awareness.** Delivered with the next real wake, or within 4h via `CC-DIGEST`. |

Precedence is `to` > `input` > `cc` — one role per seat per message. A
message with no ` — ` separator, or an unclosed `(cc`, fails closed: every
mention in it is `to`. Escalations (`deming-escalate`) and any message from
`beekeeper` always wake as `to`, regardless of position.

## Sender convention

Put the **owner** in the leading block, before the ` — `:

    @deming — ship the branch when CI's green.

**@-name** someone in the body when you want their input but they're not on
the hook for an answer:

    Decision stands as written. @nugent, does this change your sweep tier?

Use **`(cc …)`** in the leading block for pure awareness, no ask:

    @deming (cc @herschel) — merged, FYI.

Until a sender adopts this, naming the real owner only in the body gets
them classified `input` ("may decline"), not `to` — see inter#271 for the
full ruling and the coverage matrix.
