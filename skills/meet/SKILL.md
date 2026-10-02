---
name: meet
description: This skill should be used when the user asks to "run a meeting", "convene the executive team", "get the team's view on", "should we", "brainstorm with the executives", "review this with the team", "what could go wrong with", "now decide", "switch to risk mode", or invokes /executive-team:meet. Runs one executive-team meeting on a topic through the Chief of Staff, or reruns the last topic in a new mode.
argument-hint: "[brainstorm|decide|review|plan|risk] [officers: coo,cfo] <topic>"
allowed-tools: Agent, Read, Glob, Write, SendMessage, AskUserQuestion, Skill
---
Run one executive-team meeting on the topic in `$ARGUMENTS`, or rerun the previous topic in a new mode.

## Parse the arguments
1. Take the first word as the mode if it is one of `brainstorm`, `decide`, `review`, `plan`, `risk`, or if the text starts with `mode: <one of those>`. An explicit mode always wins over detection.
2. Take `officers: <codes>` (comma-separated among coo, ciso, cto, cmo, cso, cfo) as an explicit invite list if present; otherwise the invite list is automatic.
3. Treat the remaining text as the topic.
4. Mode switch: if the remaining text is empty or is only a switch phrase ("now decide", "switch to risk", "same topic, plan mode", "mode: review"), and a meeting ran earlier in this conversation, reuse that meeting's topic and pass its minutes path as `Previous meeting:`; the Chief of Staff invites the same officers and gives them their earlier answers as context. If no earlier meeting exists, ask the Owner for a topic and stop.

## Delegate to the Chief of Staff
Invoke the `executive-team:chief-of-staff` agent with exactly this instruction, filled in:

"Plugin root: ${CLAUDE_PLUGIN_ROOT}. Run a meeting. Topic: <topic>. Mode: <explicit mode, or 'detect'>. Officers: <explicit list or 'auto'>. Previous meeting: <minutes path or 'none'>. Follow your Running a meeting procedure end to end: settle the mode, invite, fan out in parallel, one consult round, synthesize the executive brief, write the minutes file, and report its path. If the mode is unclear or no officer matches at level 2 or 3, return the question for the Owner instead of a brief."

## Handle the result
- Brief returned: print it unchanged, then the minutes path. The brief's first line states the mode and how to change it; leave it in.
- Mode question returned: the agent could not tell the mode. Ask the Owner with AskUserQuestion, options brainstorm, decide, review, plan, risk, with the agent's recommendation listed first and marked "(Recommended)". Then continue the same agent with `Owner's answer: mode <choice>` when the harness supports messaging a finished agent (SendMessage); otherwise invoke `executive-team:chief-of-staff` again with the same instruction and the chosen mode.
- Officer question returned (no officer matched): show it verbatim, wait for the Owner's answer, and continue or re-invoke the same way with `Owner's answer: <answer>`.
- The agent reports it cannot use the Agent tool: run its "Running a meeting" procedure in this session, invoking the namespaced officer agents yourself with the prompts it returned.
- The Owner later states a decision: pass it to the Chief of Staff (same agent if messageable, otherwise a fresh invocation with `Record decision in <minutes path>: <decision>`).
