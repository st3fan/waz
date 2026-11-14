<!-- sdlc:managed:start -->
# Agent guidance

This repository uses **Stefan's Development Lifecycle**, the user-installed Codex skill `$sdlc`. Invoke `$sdlc bootstrap`, `$sdlc objective`, or `$sdlc intent` for lifecycle work; the detailed reusable rules are maintained in that skill, not copied into every project.

- Read `OBJECTIVE.md` (when present) before proposing significant work. It defines the project's enduring purpose and direction. Use normal GitHub Intent Issues to propose changing it.
- Keep current intent, acceptance criteria, design decisions, risks, and implementation plan **in GitHub Issue bodies**. Do not commit `intent.md`, `spec.md`, `plan.md`, or use GitHub Issue Artifacts.
- Use labels, native sub-issues/dependencies, GitHub Projects for status, and small, reviewable PRs or stacked PRs. Integrate approved safe changes into the default branch (trunk), independently of releases.
- The human approves significant decisions, start of implementation, PR merges, impactful operations, releases, and deployments separately. Never infer one approval from another.
- If `VERSIONS.md` exists, follow it for release policy. Do not create Version Issues or assume a release accompanies a merge.
- Preserve and obey the project's stricter security, testing, operational, and repository boundaries below. If generic and project-specific instructions conflict, raise the conflict rather than silently weakening safeguards.
<!-- sdlc:managed:end -->

## Project-specific agent guidance

Add repository-specific build/test commands, architecture constraints, security boundaries, and operational safeguards here. This section is never overwritten by `$sdlc bootstrap`.
