# Subagents

Use subagents where they genuinely help. Be token- and context-efficient:
a subagent starts cold and re-derives context the main session already has,
so it pays off for wide searches and independent work, not for a task the
main session can finish in two tool calls.

Pick the model by the size and stakes of the task. Use Opus for important,
large implementation work, such as building a whole PR from a spec. Use
Sonnet for searches, reviews, exploration and small fixes.
