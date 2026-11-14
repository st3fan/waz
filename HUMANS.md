<!-- sdlc:managed:start -->
# Working with Stefan's Development Lifecycle

This project uses the **`$sdlc` Codex skill**. Install it once for your user account to use it across repositories. Run Codex from the target project directory and invoke one of the following:

| What you want | What to type in Codex |
| --- | --- |
| Prepare or refresh this project | `$sdlc bootstrap` |
| Define or change project purpose and direction | `$sdlc objective` |
| Start a feature, fix, investigation, or other stream of work | `$sdlc intent` |

These are instructions to a single skill, **not shell commands** or three separate installed skills. You can add detail after the action, for example:

> `$sdlc intent Improve scan preflight reporting. Help me clarify acceptance criteria and create an Issue; don't implement yet.`

**Typical first-time setup:** `$sdlc bootstrap` → `$sdlc objective` → `$sdlc intent`. Bootstrap creates/updates `AGENTS.md` and `HUMANS.md` and preserves any custom sections. Re-run it after updating the installed skill to refresh the managed sections.

**Human decisions:** describe the desired outcome, approve significant scope/design choices, authorize implementation, review and explicitly approve PR merges. Starting a stream of work does **not** automatically authorize coding, merging, running live operations, releasing, or deploying.

**Where information lives:**
- `OBJECTIVE.md` in Git describes *why the project exists* and its enduring direction.
- GitHub Issue **bodies** contain the current intent, plans, decisions, and acceptance criteria; native sub-issues break up outcomes.
- GitHub labels classify Issues, Projects track status, PRs/stacks carry code review, and the Wiki holds reusable architectural knowledge.
- `AGENTS.md` contains project-specific agent safeguards; `VERSIONS.md` (if present) defines the project's independent release rules.

**Resuming:** give Codex the Issue number: `$sdlc intent Continue #123: read the Issue body, sub-issues, linked PRs and current status before proposing a next step.`

**Releasing:** ask Codex to inspect `VERSIONS.md` and the tested trunk commit, propose a tag and release notes, and wait for your separate approval. Merge approval is never release approval.
<!-- sdlc:managed:end -->

## Project-specific human notes

Add any local onboarding commands or project-specific review instructions here. This section is never overwritten by `$sdlc bootstrap`.
