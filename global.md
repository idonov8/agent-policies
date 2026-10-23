# Shared agent policies

These are personal defaults across projects. Follow explicit user instructions
and the current repository's more specific guidance. Keep project commands,
framework details, and domain conventions in that project's AGENTS.md.

## Website previews and publishing

- Default to local development and local previews so I can edit the files myself.
- Publish or deploy only when I explicitly request it. Creating or editing a
  website does not authorize hosting, uploads, or deployment.
- Do not push or merge to a branch that triggers deployment without that
  authorization, except when self-merging a small PR as allowed below. Skill
  defaults do not override this preference.

## Workflow and commits

- Always open a PR when a feature or fix is finished, including when working
  locally in my checkout. Work on a branch, not the default branch. Split
  independent changes into separate PRs when that makes review easier.
- During autonomous work in a cloud session or a separate worktree, commit one
  logical step at a time, with a message explaining what changed and why.
- In my local checkout while I am present, don't commit mid-task; when the work
  is finished, commit it on a branch and open the PR.
- If a PR is very small (under 20 changed lines) and you are confident in it,
  merge it yourself once tests pass. Otherwise leave it for my review.
- Preserve unrelated work already in the checkout.
- Use judgment: explain problems with a request and suggest a practical correction.

## Comments and tests

- Avoid comments that merely restate the code. Comment where intent is unclear,
  unless the repository has a stricter policy.
- Run checks appropriate to the change. Reserve E2E tests for meaningful user
  flows; a small CSS or layout fix does not need a new E2E test.

## Analytics

- In projects that already collect product analytics, use the project's wrapper;
  do not call vendor globals such as window.posthog directly in new code.
- In those projects, new user-facing features should include an exposure event
  and an outcome event. Name events snake_case, past tense for actions.
- Do not introduce a new analytics service into a project without being asked.

## Delegation

Use subagents where they help with wide searches or independent work. Be token-
and context-efficient: delegation has a cost, and a small task may be quicker in
one session. Follow the current tool's model-specific guidance when choosing a
model.
