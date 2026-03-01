# Prerequisite: Git & GitHub Collaboration Workflows

## The Objective
With a remote, distributed team of developers and traders logging into the Centralized Basement Server, ad-hoc coding will immediately lead to merge conflicts, corrupted execution states, and production crashes.

STOCKSTATS requires a military-grade Git collaboration protocol. We utilize **Trunk-Based Development** combined with strict GitHub Pull Request (PR) reviews.

---

## 1. Trunk-Based Development (The Branching Strategy)

We do not use complex GitFlow (no long-living `develop` or `release` branches). In algorithmic trading, code must move from concept to testing to production rapidly.

### 1.1 The `main` Branch (The Golden Source)
*   The `main` branch is **sacred**. It represents the physical code currently running (or capable of running) the Live Trading Engine.
*   **Direct commits to `main` are strictly prohibited.** GitHub Branch Protection rules must enforce this.

### 1.2 Feature Branches (Short-Lived)
Every single Sprint Ticket (e.g., Ticket 2.1: GARCH Math) gets its own isolated branch.
*   **Naming Convention:** `type/ticket-number-description`
    *   `feat/2.1-garch-volatility`
    *   `fix/504-rescue-loop-bug`
    *   `docs/sprint-8-readme`
*   **Lifespan:** A branch should exist for less than 48 hours. If a feature takes longer, it is too complex and must be mathematically broken down into smaller tickets.

---

## 2. The Development Loop (Using the Basement Server)

As defined in the [Remote Dev Environment](00b_remote_development_environment.md), developers write code locally but execute it via SSH on the Basement Server (`/opt/stockstats/`).

**The Workflow:**
1.  **Pull Latest:** `git checkout main && git pull origin main`
2.  **Branch Out:** `git checkout -b feat/4.1-copula-matrix`
3.  **Develop:** Write the Python Copula logic. Run tests locally on the Basement Server against the active TimescaleDB container.
4.  **Continuous Commit:**
    *   Commit logically and frequently.
    *   Commit Messages: Must follow Conventional Commits (e.g., `feat(risk): implement Clayton Copula lower-tail math`).
5.  **Push:** `git push -u origin feat/4.1-copula-matrix`

---

## 3. The GitHub Pull Request (PR) & Code Review

Code is guilty until proven innocent. No algorithm touches `main` without peer review.

### 3.1 Opening the PR
When the feature branch is pushed to GitHub, the developer opens a Pull Request against `main`.

**The PR Template Must Include:**
1.  **Linked Ticket:** "Resolves #Ticket4.1"
2.  **Mathematical Summary:** "Implemented the Numba-compiled Clayton Copula to veto trades when $\theta > 2.0$."
3.  **Validation Proof:** "Attached a screenshot of the `pytest` output proving the matrix evaluates in $< 2ms$."

### 3.2 The Code Review Rules
At least **one other human developer** (or the Principal Architect/AI) must review the code.
*   **Look for:** Edge case failures (e.g., What happens if the VWAP denominator is zero?).
*   **Performance:** Will this block the `asyncio` loop? (If yes, reject the PR).

### 3.3 The Merge
Once approved, use **Squash and Merge**. This compresses the 15 messy commits of the feature branch into one clean, atomic commit on the `main` branch, keeping the Git history perfectly readable.

---

## 4. GitHub Projects (Issue Tracking)

We map the `12_execution_sprints_and_tickets.md` directly into GitHub Issues.

1.  **The Board:** Create a standard Kanban board (To Do -> In Progress -> In Review -> Done).
2.  **The Tickets:** Every tick mark in the Strategy Sprints becomes a discrete GitHub Issue.
3.  **Assignment:** The remote developer claims the Issue, assigns themselves, and creates the corresponding branch.

---
**⬅️ Previous:** [Antigravity AI Integration](00c_antigravity_ai_integration.md) | **Next:** [Environment Management](00e_environment_management.md) ➡️
