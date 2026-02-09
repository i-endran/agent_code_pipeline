# Agent Specifications

## Overview

The pipeline consists of 6 specialized AI agents, each with a unique role in the SDLC workflow.

---

## Agent 1: SCRIBE
**Role**: Requirement Parser

| Property | Value |
|----------|-------|
| Model | gpt-4o |
| Temperature | 0.3 |
| Max Tokens | 4,000 |

### Purpose
Transforms raw requirements, user stories, or feature requests into structured feature documents.

### Inputs
- `requirement_text`: Raw requirement or user story
- `project_context`: Brief project description
- `output_format`: DOCX, Markdown, or both

### Outputs
- Structured feature document with acceptance criteria
- User story breakdown
- Edge cases and assumptions

---

## Agent 2: ARCHITECT
**Role**: Feature Doc → Plan Generator

| Property | Value |
|----------|-------|
| Model | gpt-4o |
| Temperature | 0.5 |
| Max Tokens | 8,000 |

### Purpose
Converts feature documents into detailed, actionable implementation plans.

### Inputs
- `feature_doc`: Output from SCRIBE
- `tech_stack`: Technologies in use
- `architecture_notes`: Existing architecture context
- `granularity`: Task breakdown level (1-5)

### Outputs
- `plan.md`: Step-by-step implementation plan
- File modifications list
- Test requirements
- Estimated effort

---

## Agent 3: FORGE
**Role**: Code Executor + Evaluator

| Property | Value |
|----------|-------|
| Model | claude-3-5-sonnet-20241022 |
| Temperature | 0.2 |
| Max Tokens | 16,000 |

### Purpose
Implements code changes according to the plan, runs tests, and evaluates results.

### Inputs
- `plan_md`: Output from ARCHITECT
- `repo_path`: Local repository path
- `target_branch`: Feature branch name
- `test_command`: Command to run tests
- `lint_command`: Linting command

### Outputs
- Code changes (file diffs)
- Test results
- Lint report
- Self-evaluation score

---

## Agent 4: HERALD
**Role**: MR/Patch Creator

| Property | Value |
|----------|-------|
| Model | gpt-4o-mini |
| Temperature | 0.1 |
| Max Tokens | 2,000 |

### Purpose
Creates pull/merge requests and triggers CI/CD webhooks.

### Inputs
- `git_provider`: GitHub, GitLab, or custom
- `repo_url`: Repository URL
- `mr_title_template`: Title pattern
- `reviewer_webhook_url`: CI/CD webhook
- `labels`: PR labels

### Outputs
- Created PR/MR URL
- CI/CD trigger status
- Webhook response

---

## Agent 5: SENTINEL
**Role**: Code Reviewer

| Property | Value |
|----------|-------|
| Model | gpt-4o |
| Temperature | 0.3 |
| Max Tokens | 8,000 |

### Purpose
Reviews code quality, security, and adherence to standards. Routes back to FORGE if fixes needed.

### Inputs
- `review_criteria`: Custom guidelines
- `auto_approve_threshold`: Confidence % for auto-approve
- `max_fix_iterations`: Loop limit back to FORGE
- `target_branch`: Merge target

### Outputs
- Review comments
- Approval status (APPROVED, NEEDS_CHANGES, REJECTED)
- Fix instructions (if needed)

### Behavior
```
IF review_score >= auto_approve_threshold:
    → Proceed to PHOENIX
ELSE IF iterations < max_fix_iterations:
    → Route back to FORGE with fix instructions
ELSE:
    → Flag for human review
```

---

## Agent 6: PHOENIX
**Role**: Releaser

| Property | Value |
|----------|-------|
| Model | gpt-4o-mini |
| Temperature | 0.1 |
| Max Tokens | 2,000 |

### Purpose
Manages the release process, merges to release branch, and notifies stakeholders.

### Inputs
- `release_branch`: Target branch (main, release/v*)
- `chat_webhook_url`: Slack/Teams/Zoho webhook
- `changelog_enabled`: Auto-generate changelog
- `notification_template`: Message format
- `merge_strategy`: merge, squash, rebase

### Outputs
- Merge confirmation
- Changelog (if enabled)
- Stakeholder notifications
- Release tag (optional)

---

## Configuration File

All agent configurations are stored in `backend/config/agents.yaml`:

```yaml
agents:
  scribe:
    name: "SCRIBE"
    description: "Requirement Parser"
    model: "gpt-4o"
    temperature: 0.3
    max_tokens: 4000
    system_prompt: |
      You are SCRIBE, a requirements analyst...
      
  architect:
    name: "ARCHITECT"
    # ... etc
```

## Future Extensibility

- **Admin UI**: Modify agent configs via web interface
- **Database Storage**: Persist custom configurations
- **Prompt Library**: Pre-built prompts for different domains
- **Model Marketplace**: Easy model switching and A/B testing
