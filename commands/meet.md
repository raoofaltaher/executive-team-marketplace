---
description: Run an executive-team meeting on a topic. Usage - /executive-team:meet [mode] <topic>. Modes - brainstorm, decide, review, plan, risk.
argument-hint: "[brainstorm|decide|review|plan|risk] <topic>"
---
Run an executive-team meeting.

Arguments: `$ARGUMENTS`. If the first word is one of brainstorm, decide, review, plan, risk, it is the mode and the rest is the topic. Otherwise the whole string is the topic and the mode is detected.

Delegate to the `chief-of-staff` agent with this exact instruction:

"Run a meeting. Topic: <topic>. Mode: <mode or 'detect'>. Follow your Running a meeting procedure end to end: invite, fan out in parallel, synthesize the executive brief, write the minutes file, and report its path. Ask the Owner only if no officer matches at level 2 or 3."

When the agent returns, print its brief unchanged and the minutes path. If the Owner then states a decision, send it to the same `chief-of-staff` agent to record under `## Decision`.
