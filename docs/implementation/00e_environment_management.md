# Prerequisite: Environment Management & CI/CD

## The Objective
An algorithmic trading machine that has direct API access to your retirement account cannot be tested "live in production." A single bug in a `for` loop can drain $\$50,000$ in 14 seconds.

We must adhere to the **12-Factor App Methodology**, strictly separating Configuration from Code, and physically isolating our Development, Staging, and Production environments.

---

## 1. The Three Environments

STOCKSTATS operates across three distinctly isolated topologies.

### 🟢 1. Development (DEV)
*   **Goal:** Write code, build logic, test unit functions.
*   **Physical Location:** The Centralized Basement Server (or Local MacBook).
*   **Database:** A strictly local, disposable TimescaleDB/Redis Docker network.
*   **API Keys:** Binance **Testnet** Keys OR strictly `Read-Only` Mainnet keys (for fetching historic ticks).
*   **Execution:** Blocked. The `STOCKSTATS_EXECUTION_MODE` environment variable must be set to `SHADOW` or `DISABLED`.

### 🟡 2. Staging / Paper Trading (UAT)
*   **Goal:** Forward-testing the unified system over a 30-day period using live data but mock capital to verify the $E(R)>0$ expectancy.
*   **Physical Location:** A secondary container/process on the Basement Server or a cheap Cloud VPS.
*   **Database:** A persistent Staging TimescaleDB.
*   **API Keys:** Binance **Mainnet** Keys (Read-Only). No Execution permissions allowed.
*   **Execution:** The system streams live JSON ticks, the math fires, but the Execution Router routes the trade exclusively to the local SQL `shadow_execution_ledger` (Strategy 14) to simulate slippage without risking physical capital.

### 🔴 3. Production (PROD)
*   **Goal:** deployment of Live Capital.
*   **Physical Location:** High-End AWS VPS in Tokyo (ap-northeast-1) to achieve sub-5ms arbitrage latency.
*   **Database:** Hardened RDS PostgreSQL or AWS-managed Timescale instance.
*   **API Keys:** Binance **Mainnet TRADING** Keys (Withdrawals strictly disabled at the exchange level).
*   **Execution:** Fully Live.

---

## 2. Secrets Management (Configuration)

The golden rule of Environment Management: **Never commit API Keys to Git.**

The code remains identical across all 3 environments. The *behavior* changes exclusively via environment variables injected at runtime.

### 2.1 The `.env` Hierarchy
Every environment relies on a hidden `.env` file that is listed in `.gitignore`.

**Example Dev/Staging `.env`:**
```env
STOCKSTATS_EXECUTION_MODE=SHADOW
BINANCE_API_KEY=testnet_key_or_readonly_mainnet_key
BINANCE_SECRET=testnet_secret
POSTGRES_DB=stockstats_staging
```

**Example Production `.env` (On the AWS Tokyo Server):**
```env
STOCKSTATS_EXECUTION_MODE=LIVE
BINANCE_API_KEY=MAINNET_REAL_TRADING_KEY_999xxx
BINANCE_SECRET=MAINNET_REAL_SECRET_KEY_888xxx
POSTGRES_DB=stockstats_prod
```

### 2.2 Cloud Secret Managers (Phase 7)
When deploying PROD to AWS, we will graduate from flat `.env` files to AWS Secrets Manager or GitHub Actions Secrets. The Docker container will securely pull the Binance keys into RAM only when the container boots.

---

## 3. CI/CD (Continuous Integration)

Code reviews (Sprint 00d) ensure logical accuracy, but we must use Automation to ensure mechanical stability.

### 3.1 GitHub Actions (The CI Pipeline)
When a developer pushes code to a PR, GitHub Actions automatically spins up a virtual Linux machine and executes a rigid pipeline:

1.  **Linting & Formatting:** Runs `flake8` and `black` to ensure Python code styling is identical across the distributed team.
2.  **Unit Testing (`pytest`):** Runs the mathematical validation tests. 
    *   *Example:* Feeds an isolated array of 50 integers to the Hampel Filter. If the Numba output does not exactly match the known $MAD=1.45$ truth, the test fails.
3.  **Veto:** If any CI test fails, GitHub physically blocks the "Merge" button, preventing the broken math from infecting the `main` branch.

### 3.2 Continuous Deployment (The CD Pipeline)
We will initially use Manual Deployment (SSH into the PROD server, `git pull`, `docker-compose up --build -d`). 
In Phase 7, we will upgrade to GitHub Actions CD, where merging a PR to `main` automatically tags a Release, pushes the Docker Image to AWS ECR, and forcefully restarts the Tokyo router.

---
**⬅️ Previous:** [Git & GitHub Workflows](00d_git_and_github_workflows.md) | **Next:** [Sprint 1: Core Infrastructure](01_sprint_1_infrastructure.md) ➡️
