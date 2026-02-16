# GitHub & AI Collaboration Guide

Best practices for managing multiple repositories, nested projects, and GitHub issues with AI assistance.

## 1. Multiple Tied Repositories (The "Meta-Repo" Pattern)

When working with related repositories (e.g., `ai-ops-monitoring` as the parent/umbrella and `{REPO_NAME}` as a component), you have two main strategies:

### Strategy A: Loose Coupling (Recommended for Microservices)
Treat each repo as independent. Use **GitHub Projects** to glue them together.
- **Project Board**: Create a single board at the **Organization Level** (e.g., `{GITHUB_ORG}/projects/26`).
- **Unified Views**: Add issues from both `ai-ops-monitoring` and `{REPO_NAME}` to this single board.
- **AI Workflow**:
  - When asking AI to plan, provide the **Project Board Context** (copy-paste the column status or relevant card details).
  - AI can help draft cross-repo integration tests but will need context from both codebases (you may need to checkout both locally).

### Strategy B: Git Submodules (Deprecated)

> **DEPRECATED**: This project has migrated to a monorepo structure. All components now live under `components/` in a single repository. The submodule workflow below is preserved for historical reference only.

~~Use this if `{REPO_NAME}` must be built/deployed *inside* `ai-ops-monitoring`.~~

**Current approach**: All component code lives in `components/` within the home repo. No submodule commands needed.

## 2. Cross-Repo Project Structure (Epics & Features)

**Yes, you can link multiple repos in a single Project.**
GitHub Projects (V2) are organization-level. You can pull in issues from `repo-1`, `repo-2`, and `repo-3` into the same view.

### What is an "Epic"?
In GitHub, an **Epic** is simply a **parent tracking issue**. It represents a large body of work (e.g., "Implement Multi-Cloud Support") that is too big to be completed in a single pull request. It is broken down into smaller **Feature** or **Story** issues.

### What is a "Feature"?
A **Feature** is a tangible piece of value (e.g., "Add Azure Cost API integration"). It is small enough to be implemented by a developer in a few days but large enough to require testing. Features are broken down into **Tasks** or merged via a single Pull Request.

### Defining Your Own Tags (Labels)
In GitHub, tags are called **Labels**. You can define any taxonomy you want.
1.  **Go to Issues > Labels**: In any repo, click the "Labels" button next to the search bar.
2.  **Create New Label**: Click "New label", give it a name (e.g., `Priority: High`, `Team: DevOps`), color, and description.
3.  **Syncing Labels**: GitHub doesn't auto-sync labels across repos by default. You can use:
    -   **Organization Default Labels**: Settings > Repository defaults (best for consistency).
    -   **A script**: Use the `gh` CLI to copy labels from one repo to another.

### Modeling Epics and Features
Since GitHub doesn't have native "Epics", use **Tasklists** and **Labels** to simulate the hierarchy across repos:

#### Scenario: Epic in Repo #1, Feature in Repo #2
1.  **Create the Epic**: Create an Issue in **Repo #1** (e.g., `ai-ops-monitoring`) titled "Epic: Cloud Cost Integration".
    -   Label: `Epic`
    -   Add to Project #26.
2.  **Create the Feature**: Create an Issue in **Repo #2** (e.g., `{REPO_NAME}`) titled "Feature: Azure Cost Collector".
    -   Label: `Feature`
    -   Add to Project #26.
3.  **Link Them (Parent-Child)**:
    -   Open the **Epic** issue in Repo #1.
    -   Add a Tasklist item pasting the URL of the **Feature** issue from Repo #2.
    -   *Result*: The Epic issue will show a progress bar (e.g., "1 of 5 tasks completed") tracking the status of the linked Feature issues, even though they are in different repos.

### Customizing Project Columns ("Titles")
In GitHub Projects, the columns (e.g., "Todo", "In Progress") are values of the **Status** field.
To add or rename them:
1.  **Open Project Settings**: Click the `▼` next to the active view (e.g., "Board") > **Field settings**.
2.  **Edit Status**: Click on the **Status** field.
3.  **Add/Rename Options**:
    -   Click `+` to add a new option (e.g., "In Review", "QA").
    -   Click the pencil icon to rename an existing one.
    -   *Result*: A new column appears on your board immediately.

### Adding Custom Fields
If you need more than just Status (e.g., "Estimate", "Team"), you can add **Custom Fields**:
1.  Click the `+` icon at the far right of the table headers (in Table view).
2.  Select **New field**.
3.  Choose the type: **Text**, **Number**, **Date**, **Single select**, or **Iteration**.
4.  *Example*: Create a "Size" field (Single select: S, M, L) to track feature complexity.

### Project Board Setup (Best Practices)
-   **Group by "Repository"**: In Project #26, use the "Group by" feature to see swimlanes for each repo.
-   **Custom Field "Parent Epic"**: Create a text or iteration field in the Project to manually tag the Epic ID if you need filterable views (e.g., "Epic-101").

## 3. Managing Issues with AI

### The "Issue-to-Plan" Pipeline
1. **Source Issue**: `ai-ops-monitoring/issues/123`.
2. **AI Verification**: Ask AI to read the issue and create a **Task List** in `task.md`.
3. **Implementation**: AI works on items in `task.md`.
4. **Closing**: AI generates a PR description referencing the issue (`Fixes #123`).

### Synchronization Tips
- **Labels**: Use strict labels (e.g., `component:cost-monitoring`) so AI can filter relevant issues.
- **Context injection**: If an issue depends on another repo, paste the dependent issue's content into the AI chat. "I'm working on Issue A, which depends on Issue B (pasted below...)".

## 3. Nested Repo Best Practices (Deprecated)

> **DEPRECATED**: This project uses a monorepo structure. The advice below about nested repos is no longer applicable.

With the monorepo approach, all components are in `components/` within a single repository:
- **Branching**: Single branch covers all components
- **CI/CD**: Single workflow runs on all changes
- **Docs**: Component docs can stay with components in `components/*/README.md`

## 4. AI Prompting Patterns

**Scenario: Updating a shared interface**
> "I need to update the `AgentProtocol` interface and implement it across multiple components. Please:
> 1. Plan the interface change in `components/agents/`.
> 2. Update all dependent components in the monorepo.
> 3. Verify no breaking changes across the codebase."

**Scenario: Project Board Management**
> "Here is the text dump of our refined backlog for Project 26. Please summarize the high-priority items for 'Cost Monitoring' and update my local `task.md`."

## 5. Automation (GitHub Actions)

Use GitHub Actions to reduce manual syncing:
- **Auto-add to Project**: Workflow that adds every new issue in `{REPO_NAME}` to Project 26.
- **Label Syncer**: If an issue is labeled `bug` in a child repo, add `bug` to the tracking issue in the parent repo (if using tracking issues).
