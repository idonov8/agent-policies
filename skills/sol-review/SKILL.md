---
name: sol-review
description: Run when user asks for sol review.
---

# Sol review

Run this workflow only when the user requests it. Ordinary PR work does not
activate it.

1. Identify the target PR from the user's request or current branch. Record its
   base and head commits so the review covers a known revision.
2. Delegate an independent, read-only review to **GPT-6.1 Sol**
   (`gpt-6.1-sol`). Give it the diff, repository instructions, relevant source
   files, and validation results. Ask for actionable correctness, regression,
   and missing-test findings with file/line references and supporting evidence.
   Keep the reviewer from editing files or publishing comments.
3. Assess each finding against the code. Fix valid issues within the task's
   scope and explain any dismissed findings. Run checks appropriate to the
   fixes, then commit and update the PR under the repository's usual workflow.
4. Only treat the PR as ready for the user's review after the Sol review and
   this response to its findings are complete. Summarize the reviewed revision,
   findings addressed or dismissed, validation, and any remaining issues. If
   fixes materially change the reviewed behavior, have Sol review those changes
   before handoff.

If GPT-6.1 Sol cannot be selected or the review cannot finish, report that the
review step remains incomplete. Do not silently substitute another model or
claim the PR has passed this workflow.
