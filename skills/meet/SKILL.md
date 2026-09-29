---
name: meet
description: This skill should be used when the user asks to "run a meeting", "convene the executive team", "get the team's view on", "should we", "brainstorm with the executives", "review this with the team", or invokes /executive-team:meet. Runs one executive-team meeting on a topic through the Chief of Staff.
argument-hint: "[brainstorm|decide|review|plan|risk] [officers: coo,cfo] <topic>"
allowed-tools: Agent, Read, Glob, Write, SendMessage, Skill
---
Run one executive-team meeting on the topic in `$ARGUMENTS`.

## Parse the arguments
1. Take the first word as the mode if it is one of `brainstorm`, `decide`, `review`, `plan`, `risk`; otherwise leave the mode to be detected.
2. Take `officers: <codes>` (comma-separated among coo, ciso, cto, cmo, cso, cfo) as an explicit invite list if present; otherwise the invite list is automatic.
3. Treat the remaining text as the topic. If the topic is empty, ask the Owner for one and stop.

## Delegate to the Chief of Staff
Invoke the `executive-team:chief-of-staff` agent with exactly this instruction, filled in:

"Plugin root: ${CLAUDE_PLUGIN_ROOT}. Run a meeting. Topic: <topic>. Mode: <mode or 'detect'>. Officers: <explicit list or 'auto'>. Follow your Running a meeting procedure end to end: invite, fan out in parallel, one consult round, synthesize the executive brief, write the minutes file, and report its path. If no officer matches at level 2 or 3, return the question for the Owner instead of a brief."

## Handle the result
- Brief returned: print it unchanged, then the minutes path.
- Question returned (no officer matched): show it verbatim and wait for the Owner's answer. Continue the same agent with the answer when the harness supports messaging a finished agent (SendMessage); otherwise invoke `executive-team:chief-of-staff` again with the same instruction plus `Owner's answer: <answer>`.
- The agent reports it cannot use the Agent tool: run its "Running a meeting" procedure in this session, invoking the namespaced officer agents yourself with the prompts it returned.
- The Owner later states a decision: pass it to the Chief of Staff (same agent if messageable, otherwise a fresh invocation with `Record decision in <minutes path>: <decision>`).
