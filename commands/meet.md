---
description: Run an executive-team meeting on a topic. Usage - /executive-team:meet [mode] [officers: coo,cfo] <topic>. Modes - brainstorm, decide, review, plan, risk.
argument-hint: "[brainstorm|decide|review|plan|risk] [officers: coo,cfo] <topic>"
---
Run an executive-team meeting.

Arguments: `$ARGUMENTS`. If the first word is one of brainstorm, decide, review, plan, risk, it is the mode. If the text contains `officers: <codes>` (comma-separated position codes among coo, ciso, cto, cmo, cso, cfo), that is an explicit officer list and the Chief of Staff invites exactly those. Everything else is the topic. If no mode is given, the mode is detected.

Delegate to the `executive-team:chief-of-staff` agent with this exact instruction:

"Plugin root: ${CLAUDE_PLUGIN_ROOT}. Run a meeting. Topic: <topic>. Mode: <mode or 'detect'>. Officers: <explicit list or 'auto'>. Follow your Running a meeting procedure end to end: invite, fan out in parallel, one consult round, synthesize the executive brief, write the minutes file, and report its path. If no officer matches at level 2 or 3, return the question for the Owner instead of a brief."

Then:
- If the agent returns a brief, print it unchanged and the minutes path.
- If the agent returns a question instead of a brief (no officer matched), show the question verbatim, wait for the Owner's answer, and send that answer to the same agent with SendMessage so it continues the meeting.
- If the agent reports that it cannot use the Agent tool, run its "Running a meeting" procedure yourself in this session using the prompts it returned, with the same namespaced officer agents.
- If the Owner then states a decision, send it to the same agent to record under `## Decision`.
