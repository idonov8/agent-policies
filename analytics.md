# Analytics

Go through the project's own analytics wrapper. Never call `window.posthog`
or an equivalent vendor global directly in new code.

Every new user-facing feature ships with two events: an **exposure** (the
user saw or entered it) and an **outcome** (the thing the feature should
cause).

Name events `snake_case`, past tense for actions.
