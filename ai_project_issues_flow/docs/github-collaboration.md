# GitHub & AI Collaboration Guide

Best practices for managing multiple repositories, nested projects, and GitHub issues with AI assistance.

## 1. Multiple Tied Repositories (The "Meta-Repo" Pattern)

When working with related repositories (e.g., a parent/umbrella repo and component repos), you have two main strategies:

### Strategy A: Loose Coupling (Recommended for Microservices)
Treat each repo as independent. Use **GitHub Projects** to glue them together.
- **Project Board**: Create a single board at the **Organization Level** (e.g., `{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}`).
- **Unified Views**: Add issues from multiple repos to this single board.
- **AI Workflow**:
  - When asking AI to plan, provide the **Project Board Context** (copy-paste the column status or relevant card details).
  - AI can help draft cross-repo integration tests but will need context from both codebases (you may need to checkout both locally).

### Strategy B: Monorepo (Recommended for Small Teams)
Use a single repository with all components under `components/`.
- **Branching**: Single branch covers all components
- **CI/CD**: Single workflow runs on all changes
- **Docs**: Component docs stay with components in `components/*/README.md`

## 2. Cross-Repo Project Structure (Epics & Features)

**Yes, you can link multiple repos in a single Project.**
GitHub Projects (V2) are organization-level. You can pull in issues from multiple repos into the same view.

### What is an "Epic"?
In GitHub, an **Epic** is simply a **parent tracking issue**. It represents a large body of work that is too big to be completed in a single pull request. It is broken down into smaller **Feature** or **Story** issues.

### What is a "Feature"?
A **Feature** is a tangible piece of value. It is small enough to be implemented by a developer in a few days but large enough to require testing. Features are broken down into **Tasks** or merged via a single Pull Request.

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
1.  **Create the Epic**: Create an Issue in **Repo #1** titled "Epic: {Epic Name}".
    -   Label: `Epic`
    -   Add to Project Board.
2.  **Create the Feature**: Create an Issue in **Repo #2** titled "Feature: {Feature Name}".
    -   Label: `Feature`
    -   Add to Project Board.
3.  **Link Them (Parent-Child)**:
    -   Open the **Epic** issue in Repo #1.
    -   Add a Tasklist item pasting the URL of the **Feature** issue from Repo #2.
    -   *Result*: The Epic issue will show a progress bar tracking the status of linked Feature issues, even across repos.

### Customizing Project Columns
In GitHub Projects, the columns (e.g., "Todo", "In Progress") are values of the **Status** field.
To add or rename them:
1.  **Open Project Settings**: Click the `▼` next to the active view > **Field settings**.
2.  **Edit Status**: Click on the **Status** field.
3.  **Add/Rename Options**:
    -   Click `+` to add a new option (e.g., "In Review", "QA").
    -   Click the pencil icon to rename an existing one.

### Adding Custom Fields
If you need more than just Status (e.g., "Estimate", "Team"), you can add **Custom Fields**:
1.  Click the `+` icon at the far right of the table headers (in Table view).
2.  Select **New field**.
3.  Choose the type: **Text**, **Number**, **Date**, **Single select**, or **Iteration**.
4.  *Example*: Create a "Size" field (Single select: S, M, L) to track feature complexity.

### Project Board Setup (Best Practices)
-   **Group by "Repository"**: Use the "Group by" feature to see swimlanes for each repo.
-   **Custom Field "Parent Epic"**: Create a text field to manually tag the Epic ID for filterable views.

## 3. Managing Issues with AI

### The "Issue-to-Plan" Pipeline
1. **Source Issue**: `{GITHUB_ORG}/{REPO_NAME}/issues/{ISSUE_NUMBER}`.
2. **AI Verification**: Ask AI to read the issue and create a **Task List** in `task.md`.
3. **Implementation**: AI works on items in `task.md`.
4. **Closing**: AI generates a PR description referencing the issue (`Fixes #{ISSUE_NUMBER}`).

### Synchronization Tips
- **Labels**: Use strict labels (e.g., `component:{component-name}`) so AI can filter relevant issues.
- **Context injection**: If an issue depends on another repo, paste the dependent issue's content into the AI chat.

## 4. AI Prompting Patterns

**Scenario: Updating a shared interface**
> "I need to update the `{InterfaceName}` interface and implement it across multiple components. Please:
> 1. Plan the interface change in `components/{component}/`.
> 2. Update all dependent components in the monorepo.
> 3. Verify no breaking changes across the codebase."

**Scenario: Project Board Management**
> "Here is the text dump of our refined backlog for Project {PROJECT_BOARD_NUMBER}. Please summarize the high-priority items for '{Component Name}' and update my local `task.md`."

## 5. Automation (GitHub Actions)

Use GitHub Actions to reduce manual syncing:
- **Auto-add to Project**: Workflow that adds every new issue in `{REPO_NAME}` to the Project Board.
- **Label Syncer**: If an issue is labeled `bug` in a child repo, auto-sync the label to tracking issues.

---

## Template Usage

This document uses placeholder variables from [CONFIG.md](../CONFIG.md):
- `{GITHUB_ORG}` — Your GitHub organization
- `{REPO_NAME}` — Repository name
- `{PROJECT_BOARD_NUMBER}` — GitHub Project V2 board number
