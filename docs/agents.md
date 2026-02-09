# Agent Specifications

## Overview

The pipeline consists of 5 specialized AI agents (HERALD removed, functionality merged into SENTINEL), each with a unique role in the SDLC workflow. All agents now use **Google Gemini** models and include **automatic state capture** for full audit trails.

---

## Agent 1: SCRIBE
**Role**: Requirement Parser & Document Generator

| Property | Value |
|----------|-------|
| Model | gemini-2.0-flash |
| Provider | Google |
| Temperature | 0.3 |
| Max Tokens | 8,000 |

### Purpose
Transforms raw requirements, user stories, or feature requests into structured SDLC documents.

### Inputs
- `requirement_text`: Raw requirement or user story
- `project_context`: Brief project description or repository URL
- `output_format`: Markdown (default)
- `selected_documents`: List of document types to generate
  - `feature_doc`: Feature specification
  - `dpia`: Data Privacy Impact Assessment
  - `data_flow`: Data flow diagrams

### Outputs
- Structured feature document with acceptance criteria
- DPIA (if selected)
- Data flow documentation (if selected)
- All outputs saved to `storage/artifacts/task_{id}/`

### Guardrails
- Do not include PII in documents
- Always structure output as markdown

### Audit Trail
✅ **State Snapshot**: Captured automatically on every execution  
✅ **Queryable**: Via `/api/audit/task/{task_id}` or `/api/audit/state/{state_id}`

---

## Agent 2: ARCHITECT
**Role**: Technical Planning & Repository Analysis

| Property | Value |
|----------|-------|
| Model | gemini-2.0-pro-exp-02-05 |
| Provider | Google |
| Temperature | 0.4 |
| Max Tokens | 16,000 |

### Purpose
Analyzes cloned repositories and converts feature documents into detailed, actionable implementation plans.

### Inputs
- `feature_doc`: Output from SCRIBE (auto-loaded)
- `repo_path`: Cloned repository path (auto-provided)
- `tech_stack`: Technologies in use
- `architecture_notes`: Existing architecture context
- `granularity`: Task breakdown level (1-5)

### Outputs
- `plan.md`: Step-by-step implementation plan
- File modifications list
- Technical approach and patterns
- Saved to `storage/artifacts/task_{id}/implementation_plan.md`

### Tools
- `read_file`: Read repository files
- `list_dir`: Explore directory structure
- `grep_search`: Search codebase

### Guardrails
- Analyze README.md and existing code before planning
- Do not request info available in the codebase

### Audit Trail
✅ **State Snapshot**: Captured automatically on every execution  
✅ **Queryable**: Via `/api/audit/task/{task_id}` or `/api/audit/state/{state_id}`

---

## Agent 3: FORGE
**Role**: Code Executor + Git Commit Manager

| Property | Value |
|----------|-------|
| Model | gemini-2.0-flash |
| Provider | Google |
| Temperature | 0.2 |
| Max Tokens | 16,000 |

### Purpose
Implements code changes according to the plan, runs tests, and commits with **full audit metadata**.

### Inputs
- `plan_md`: Output from ARCHITECT (auto-loaded)
- `repo_path`: Local repository path (auto-provided)
- `target_branch`: Feature branch name (auto-created)
- `test_command`: Command to run tests (e.g., `npm test`)
- `lint_command`: Linting command (e.g., `npm run lint`)
- `commit_rules`: Git commit configuration
  - `strategy`: `per_step` or `bulk`
  - `prefix`: Commit message prefix (default: `[FORGE-AI]`)
  - `include_metadata`: Embed agent state in commits (default: `true`)

### Outputs
- Code changes (committed to branch)
- Test results
- Lint report
- **Git commits with embedded metadata**:
  ```
  [FORGE-AI] Implemented feature
  
  Agent-State-ID: {uuid}
  Model: gemini-2.0-flash
  Temperature: 0.2
  Task: {task_id}
  Timestamp: {iso_timestamp}
  Provider: google
  ```

### Tools
- `edit_file`: Modify code files
- `run_cmd`: Execute shell commands
- `test`: Run test suites

### Guardrails
- Always run tests after code changes
- Do not delete files unless explicitly planned

### Audit Trail
✅ **State Snapshot**: Captured automatically on every execution  
✅ **Git Metadata**: Agent state embedded in every commit  
✅ **Queryable**: Via `/api/audit/commit/{commit_hash}` to trace commit → agent config

---

## Agent 4: SENTINEL
**Role**: Code Reviewer & MR Creator

| Property | Value |
|----------|-------|
| Model | gemini-2.0-pro-exp-02-05 |
| Provider | Google |
| Temperature | 0.3 |
| Max Tokens | 8,000 |

### Purpose
Reviews code quality, security, and adherence to standards. Creates MRs or routes back to FORGE if fixes needed.

**Note**: HERALD functionality has been merged into SENTINEL.

### Inputs
- `review_criteria`: Custom guidelines
- `auto_approve_threshold`: Confidence % for auto-approve (default: 85)
- `max_fix_iterations`: Loop limit back to FORGE (default: 3)
- `target_branch`: Merge target (e.g., `develop`)

### Outputs
- Review comments (saved to `storage/artifacts/task_{id}/review.json`)
- Approval status: `APPROVED`, `NEEDS_CHANGES`, `REJECTED`
- Fix instructions (if needed)
- MR/PR URL (if approved)
- Local diff patch (saved to `storage/artifacts/task_{id}/patch.diff`)

### Tools
- `read_diff`: Analyze code changes
- `create_mr`: Create merge request
- `comment`: Add review comments

### Behavior
```
IF review_score >= auto_approve_threshold:
    → Create MR and proceed to PHOENIX
ELSE IF iterations < max_fix_iterations:
    → Route back to FORGE with fix instructions
ELSE:
    → Flag for human review
```

### Guardrails
- Focus on security and code quality
- Verify that all acceptance criteria from SCRIBE are met

### Audit Trail
✅ **State Snapshot**: Captured automatically on every execution  
✅ **Queryable**: Via `/api/audit/task/{task_id}` or `/api/audit/state/{state_id}`

---

## Agent 5: PHOENIX
**Role**: Release Manager

| Property | Value |
|----------|-------|
| Model | gemini-2.0-flash |
| Provider | Google |
| Temperature | 0.1 |
| Max Tokens | 4,000 |

### Purpose
Manages the release process, merges to release branch, and notifies stakeholders.

### Inputs
- `release_branch`: Target branch (main, release/v*)
- `chat_platform`: Slack, Teams, or Zoho Cliq
- `chat_webhook_url`: Notification webhook
- `changelog_enabled`: Auto-generate changelog (default: `true`)
- `notification_template`: Message format
- `merge_strategy`: merge, squash, rebase

### Outputs
- Merge confirmation
- Changelog (if enabled)
- Stakeholder notifications
- Release tag (optional)

### Tools
- `merge`: Merge branches
- `notify`: Send notifications
- `resolve_conflict`: Handle merge conflicts

### Guardrails
- Do not merge if there are unresolved conflicts without user input

### Audit Trail
✅ **State Snapshot**: Captured automatically on every execution  
✅ **Queryable**: Via `/api/audit/task/{task_id}` or `/api/audit/state/{state_id}`

---

## Audit Trail System (Phase 2D)

### Overview
Every agent execution is automatically tracked with a complete configuration snapshot for compliance and reproducibility.

### What Gets Captured
For **every agent** (SCRIBE, ARCHITECT, FORGE, SENTINEL, PHOENIX):
- Model name and provider
- Temperature, max_tokens
- Guardrails and policies
- Enforcement prompts
- Tools list
- User-provided prompt
- Execution timestamp
- Task ID

### Storage
- **Database**: `agent_execution_logs` table
- **Artifacts**: JSON snapshots in `storage/audit/task_{id}/agent_state_{uuid}.json`

### Query APIs
```bash
# Get all agent executions for a task
GET /api/audit/task/{task_id}

# Get full agent config by state ID
GET /api/audit/state/{state_id}

# Find agent state from Git commit (Forge only)
GET /api/audit/commit/{commit_hash}
```

### Benefits
✅ **Full Reproducibility**: Re-execute with exact historical config  
✅ **Compliance**: Complete audit trail for regulatory requirements  
✅ **Debugging**: Know which hyperparameters generated specific outputs  
✅ **Rollback Safety**: Trace any code change to agent state

---

## Configuration File

All agent configurations are stored in `backend/config/agents.yaml`:

```yaml
agents:
  scribe:
    name: "SCRIBE"
    model: "gemini-2.0-flash"
    provider: "google"
    temperature: 0.3
    max_tokens: 8000
    guardrails:
      - "Do not include PII in documents"
      - "Always structure output as markdown"
    policies:
      output_validation: true
      max_retries: 2
    enforcement_prompt: |
      You MUST produce structured markdown with these sections:
      - Summary, Functional Requirements, Non-Functional Requirements, Acceptance Criteria
      
  forge:
    name: "FORGE"
    model: "gemini-2.0-flash"
    provider: "google"
    temperature: 0.2
    max_tokens: 16000
    commit_rules:
      strategy: "per_step"
      prefix: "[FORGE-AI]"
      include_metadata: true
      signature_format: "Agent-State-ID: {state_id}\nModel: {model}\nTemperature: {temperature}"
```

## Future Extensibility

- **Admin UI**: Modify agent configs via web interface (Phase 3)
- **Model Marketplace**: Easy model switching and A/B testing
- **Custom Tools**: MCP server integration for agent-specific tools (Phase 4)
- **Human-in-the-Loop**: Approval workflows at each stage (Phase 5)
