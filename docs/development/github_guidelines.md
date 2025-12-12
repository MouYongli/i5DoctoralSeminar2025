# GitHub Workflow with Claude Code

This document provides comprehensive guidance for using Claude Code with Git and GitHub workflows, including milestones, issues, branches, commits, and pull requests.

## Table of Contents

- [Overview](#overview)
- [Project Setup](#project-setup)
- [Milestone Management](#milestone-management)
- [Issue Management](#issue-management)
- [Branch Workflow](#branch-workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Using gh CLI with Claude Code](#using-gh-cli-with-claude-code)
- [Example Workflows](#example-workflows)
- [Best Practices](#best-practices)

## Overview

Claude Code integrates seamlessly with Git and GitHub workflows, helping you manage your development process efficiently. The `github-workflow-manager` agent can assist with:

- Creating and tracking milestones
- Managing issues and their lifecycle
- Following branch naming conventions
- Writing clear commit messages
- Creating comprehensive pull requests

## Project Setup

### Prerequisites

1. **Git**: Ensure Git is installed and configured
   ```bash
   git --version
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **GitHub CLI (gh)**: Install and authenticate
   ```bash
   gh --version
   gh auth login
   ```

3. **Repository Access**: Ensure you have proper permissions for the repository

## Milestone Management

### Creating Milestones

Milestones help organize work into time-bound goals. Use the `.github/MILESTONE_TEMPLATE.md` template when planning. You can plan the milestone by writing a plan in the `MILESTONE_PLAN.md` file.

**Note**: The milestone title should be provided as a command-line argument, while `MILESTONE_PLAN.md` is used only for the detailed description.

```bash
# Create a new milestone
gh api repos/:owner/:repo/milestones -f title="Sprint 5 - 2024-03" -f description="$(cat MILESTONE_PLAN.md)" -f due_on="2024-03-31T23:59:59Z"
```

**Milestone Template Structure:**
- Title format: `[Version] Feature Name` or `Sprint N - YYYY-MM`
- Timeline with start/due dates
- Clear description and success criteria
- Task list with checkboxes
- Risk assessment

### Monitoring Milestones

**Note**: In the commands below, replace `{milestone_number}`, `{issue_number}`, `{pr_number}`, and similar placeholders with actual numeric values.

```bash
# List all milestones
gh api repos/:owner/:repo/milestones --jq '.[] | {number: .number, title: .title, due_on: .due_on, open_issues: .open_issues}'

# Get detailed milestone information
gh api repos/:owner/:repo/milestones/{milestone_number} --jq '{title: .title, description: .description, open_issues: .open_issues, closed_issues: .closed_issues, due_on: .due_on}'

# List issues in a milestone
gh api "repos/:owner/:repo/issues?milestone={milestone_number}&state=all" --jq '.[] | {number: .number, title: .title, state: .state, assignee: .assignee.login}'

# List open issues in a milestone
gh api "repos/:owner/:repo/issues?milestone={milestone_number}&state=open" --jq '.[] | {number: .number, title: .title, state: .state, assignee: .assignee.login}'
```

### Updating Milestones

```bash
# Update milestone due date
gh api repos/:owner/:repo/milestones/{milestone_number} -X PATCH -f due_on="2024-04-15T23:59:59Z"

# Update milestone description
gh api repos/:owner/:repo/milestones/{milestone_number} -X PATCH -f description="$(cat MILESTONE_PLAN.md)"

# Close a completed milestone
gh api repos/:owner/:repo/milestones/{milestone_number} -X PATCH -f state="closed"
```

## Issue Management

### Creating Issues

Issues should be well-structured with clear acceptance criteria.  Use the `.github/ISSUE_TEMPLATE/<issue-type>.md` template when planning. You can plan the issue by writing a plan in the `ISSUE_PLAN.md` file.

**Using gh CLI:**
```bash
# Create a new issue
gh issue create --title "[Feature] Add user authentication system" --body "$(cat ISSUE_PLAN.md)" --label "enhancement" --milestone "Sprint 5"
```

**Issue Best Practices:**
- **Title Format**: `[Type] Clear, actionable description`
  - Types: `Feature`, `Bug`, `Docs`, `Refactor`, `Test`, `Chore`, `Infra`
- **Description**: Include context, requirements, and acceptance criteria
- **Labels**: Apply appropriate labels (bug, enhancement, documentation, priority, etc.)
- **Milestone**: Assign to relevant milestone
- **Assignees**: Tag responsible team members

### Viewing and Managing Issues

```bash
# List open issues assigned to you
gh issue list --assignee @me --state open

# View specific issue details
gh issue view {issue_number}

# Update issue status
gh issue close {issue_number}
gh issue reopen {issue_number}

# Add labels to issue
gh issue edit {issue_number} --add-label "priority:high"

# Assign issue to milestone
gh issue edit {issue_number} --milestone "Sprint 5"
```

### Issue Linking

Link issues to show dependencies. Use the `Closes #123`, `Fixes #456`, `Relates to #789` keywords in the issue description or comments.

## Branch Workflow

### Branch Naming Conventions

Follow this standardized naming pattern:
```
<type>/<issue-number>-<brief-description>
```

**Types:**
- `feature/` - New features
- `enhancement/` - Enhancements to existing features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring
- `infra/` - Infrastructure changes (e.g. configuration changes, deployment updates, etc.)
- `docs/` - Documentation updates
- `test/` - Test additions or updates
- `chore/` - Build, CI, or tooling changes

**Examples:**
```
feature/123-user-authentication
bugfix/456-fix-login-redirect
docs/789-update-api-documentation
refactor/101-optimize-database-queries
```

### Creating Branches

```bash
# Create and checkout a new feature branch
git checkout -b feature/123-user-authentication
# Push new branch to remote
git push -u origin feature/123-user-authentication
```

### Branch Management

```bash
# List all branches
git branch -a

# Switch between branches
git checkout branch-name

# Update branch with latest main
git checkout feature/123-user-authentication
git pull origin main

# Delete local branch
git branch -d feature/123-user-authentication

# Delete remote branch
git push origin --delete feature/123-user-authentication
```

## Commit Guidelines

### Conventional Commits Format

Use the conventional commits specification:
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `infra` - Infrastructure changes
- `style` - Code style changes (formatting, no logic changes)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Build process, tooling, dependencies

**Examples:**
```bash
git commit -m "feat(auth): add JWT token validation"
git commit -m "infra(env.prod): update production environment configuration"
git commit -m "fix(api): resolve null pointer in user endpoint"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(database): optimize query performance"
```

### Commit Best Practices

1. **Keep commits atomic**: One logical change per commit
2. **Write clear messages**: Use present tense, imperative mood
3. **Reference issues**: Include issue numbers in commit body
4. **Keep commits focused**: Don't mix unrelated changes

**Multi-line commit example:**
```bash
git commit -m "$(cat <<'EOF'
feat(scheduler): implement shift assignment algorithm

- Add constraint solver for shift assignments
- Implement nurse availability checking
- Add unit tests for scheduling logic

Closes #123
EOF
)"
```

### Viewing Commit History

```bash
# View recent commits
git log --oneline -10

# View commits with details
git log --graph --decorate --all

# View commits for specific file
git log --follow -- path/to/file

# View commits by author
git log --author="Your Name"
```

## Pull Request Process

### Creating Pull Requests

Use the `.github/PULL_REQUEST_TEMPLATE.md` for consistent PR structure. You can plan the PR by writing a plan in the `PULL_REQUEST_PLAN.md` file.

**Using gh CLI:**
```bash
# Create PR from current branch
gh pr create --title "feat: Add user authentication system" --body "$(cat PULL_REQUEST_PLAN.md)"
```

**PR Title Format:**
```
<type>: Brief description of changes

Examples:
feat: Add user authentication system
fix: Resolve login redirect issue
docs: Update API documentation
refactor: Optimize database queries
```

### PR Description Structure

Follow the template structure:
1. **Description**: Clear overview of changes
2. **Type of Change**: Check applicable boxes
3. **Related Issues**: Link with `Closes #123`, `Fixes #456`
4. **Changes Made**: Bullet list of key changes
5. **Testing Approach**: How changes were tested
6. **Checklist**: Pre-review verification
7. **Screenshots**: For UI changes
8. **Additional Notes**: Any other context

### Managing Pull Requests

```bash
# List open PRs
gh pr list --state open

# View specific PR
gh pr view {pr_number}

# Check PR status and checks
gh pr checks {pr_number}

# Review PR
gh pr review {pr_number} --approve
gh pr review {pr_number} --comment --body "Looks good!"
gh pr review {pr_number} --request-changes --body "Please address..."

# Merge PR
gh pr merge {pr_number} --squash
gh pr merge {pr_number} --merge
gh pr merge {pr_number} --rebase
```

### PR Best Practices

1. **Keep PRs focused**: One feature or fix per PR
2. **Write comprehensive descriptions**: Help reviewers understand context
3. **Link issues**: Use closing keywords
4. **Add tests**: Include test coverage for changes
5. **Update documentation**: Keep docs in sync with code
6. **Self-review**: Review your own changes before requesting review
7. **Respond to feedback**: Address comments promptly and professionally

## Best Practices

### General Guidelines

1. **Use the github-workflow-manager agent**: Let Claude Code help manage your workflow
2. **Follow naming conventions**: Consistent branch and commit naming
3. **Keep work focused**: One issue per branch, atomic commits
4. **Link everything**: Connect commits, branches, PRs, and issues
5. **Document thoroughly**: Clear descriptions in issues and PRs
6. **Test before pushing**: Ensure code works and tests pass
7. **Review your own code**: Self-review before requesting team review
8. **Respond promptly**: Address review feedback quickly
