# Prerequisite: Antigravity AI Integration & Collaboration

## The Objective
STOCKSTATS is not being built by a siloed human team. It is a cooperative endeavor between human domain experts and the **Antigravity AI Agent**. 

To maximize velocity and prevent architectural drift, the engineering team must follow specific protocols when interfacing with the AI.

---

## 1. The Role of the Antigravity Agent

The AI operates as the **Principal Engineer & Executor**. 
It is capable of reading the entire repository context, executing bash commands, scaffolding Next.js architectures, writing Numba JIT-compiled mathematics, and verifying PostgreSQL schemas.

### What the AI Does Best:
*   **Boilerplate & Scaffolding:** Generating `docker-compose.yml`, GitHub Actions, and React component structures.
*   **Mathematical Implementation:** Translating the theoretical formulas from the `docs/models/` directory into highly optimized Python/Numba code.
*   **Debugging Complex State:** Tracing `HTTP 504 Orphan` logic across the Execution Router and the PostgreSQL ledger.
*   **Documentation:** Keeping these Markdown files mathematically synchronized with the actual codebase.

### What Humans Do Best:
*   **Domain Expertise (Ground Truth):** Defining the specific crypto asset universe, recognizing hidden order-book toxicity, and defining the specific $E(R)>0$ statistical edge.
*   **Strategic Direction:** Prioritizing which Sprints to execute and defining the strict Risk Management constraints (e.g., "Cap Kelly sizing to 5%").

---

## 2. Collaboration Protocols

To prevent the AI from generating "hallucinated" code or deviating from the physical strategy, the team must adhere to the following interaction loop:

### 2.1 Context Injection (The "Tell Me" Rule)
The AI is powerful, but it cannot read your mind. When assigning a ticket to the AI (e.g., "Build the Hampel Filter"):
1.  **Reference the Docs:** Explicitly tell the AI which file to read first. (e.g., *"Read `docs/implementation/03_sprint_3_hampel_filter.md` and execute Step 1."*)
2.  **Define the Scope:** Do not ask the AI to "build Phase 1." Ask it to "Execute Ticket 1.4: The CCXT Async WebSocket Ingestor." Granularity prevents code spaghetti.

### 2.2 The "View File" Verification Loop
Before asking the AI to modify a complex file (like `stream.py`), always prompt it to view the current state:
*"Please review the current logic in `backend/ingestion/stream.py` and then inject the VWAP Aggregation logic from Sprint 2."*

### 2.3 Task Boundaries (Planning vs. Execution)
The AI operates in explicit modes. 
*   **Planning Mode:** The AI writes these Markdown documents and updates `task.md`. It does not write `.py` files.
*   **Execution Mode:** The AI opens the terminal, writes physical code, and commits to Git. 

Always confirm which mode you are operating in before issuing a command. If the AI is planning, do not ask it to suddenly deploy a Docker container. 

---

## 3. The Implementation Handoff

When the human team is ready to begin a Sprint, the workflow is:

1.  **Human:** *"We are starting Sprint 1. Please read `01_sprint_1_infrastructure.md`."*
2.  **AI:** Evaluates the requirements, proposes the exact Bash commands or Python file creations required.
3.  **Human:** *"Approved. Switch to Execution Mode and build the Docker architecture."*
4.  **AI:** Generates the `docker-compose.yml`, writes `.env` placeholders, runs `docker-compose up -d`, and verifies the containers are running via the terminal.
5.  **AI:** Commits the clean scaffold to Git.

---
**⬅️ Previous:** [Implementation Index](00_implementation_index.md) | **Next:** [Git & GitHub Workflows](00d_git_and_github_workflows.md) ➡️
