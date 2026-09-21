# Subagents

Use subagents where they genuinely help. Be token- and context-efficient:
a subagent starts cold and re-derives context the main session already has,
so it pays off for wide searches and independent work, not for a task the
main session can finish in two tool calls.

Never use Opus for subagents. Sonnet is sufficient for implementation,
review, and exploration. Opus is for planning only.
