
# Recall

The Ledger schema and all definitions are in the [Coordinator's instructions](../SKILL.md).

## Procedure

1. **Assess.** Check whether a Ledger block exists in your current context. Note what is present and what is missing.

2. **Find sources.** Scan for readable conversation history: prior turns in context, transcript files on disk, agent transcript files, prior compaction summaries.

3. **Extract.** From each source, identify Attention Surfaces and Proposals. Classify using the tells and statuses defined in the [Coordinator](../SKILL.md). Preserve each Proposal's Content at its established Specificity.

4. **Reconstruct.** Build the Ledger block in the [sentinel format](../SKILL.md#the-ledger). Preserve prior IDs where they exist.

5. **Report.** One or two sentences: what you recovered and any specific gap.

## Hard rules

- Never invent a Proposal you cannot substantiate from the sources you read.
- An empty recovery stated plainly is correct. A plausible reconstruction is not.
- Ambiguous status defaults to Open.
