---
name: sol-review
description: Run when user asks for sol review.
---

# Sol review

Run this workflow only when the user requests it. Ordinary PR work does not
activate it.

- Run a review by GPT-6.1 Sol for the PR. Address the comments it gives. You can run up to 3 rounds of review if needed. In the first one Sol looks over all the PR, later rounds only address your changes and responses.
- Use Codex CLI or fleet to run the Sol agents.
- Ignore nitpicks and things that are not related to the goal of the PR. It's ok to decide against a reccommendation from Sol. The point to get help from it to flag things you may have missed. 
- Post the review process as comments on the PR so it's clear to see the process you went through.