# STOCKSTATS: Project Vision & Scope

## 1. Executive Summary
The **STOCKSTATS** system is a proprietary, internally-developed algorithmic quantitative trading platform designed exclusively for our team. It is strictly not a commercial Software-as-a-Service (SaaS) product. 

Its primary mathematical mandate is to execute purely quantitative trading strategies—specifically focusing on **Statistical Arbitrage (Pairs Trading)**, **Mean Reversion**, and **Intraday Volatility Profiling**—across global equities and cryptocurrency liquidity pools, ensuring a mathematically proven, positive expected value ($E(R) > 0$).

Crucially, the system is designed as a **comprehensive operational platform**, not just a trading script. It is being developed through a strictly phased architectural roadmap (see `00_roadmap.md`). It initially serves as a highly advanced manual signal terminal, maturing linearly into a fully autonomous, Machine-Learning-overlayed algorithmic engine. 

Throughout all phases, STOCKSTATS acts as the central hub for the proprietary trading desk: tracking individual quantitative researcher performance, enforcing unyielding portfolio risk limits, and providing a unified operations dashboard.

## 2. Core Operational Mandates

### A. The Proprietary Edge
The logic engine, mathematical models, and latency-sensitive execution algorithms are strictly internal. The infrastructure must be aggressively secure, self-hosted (or securely managed in isolated cloud VPCs), and built fundamentally to protect our algorithmic "edge." Third-party dependencies are minimized to prevent intellectual property leakage.

### B. The $E(R) > 0$ Intelligence Engine
The system does not guess. The absolute core of STOCKSTATS is the automated mathematical identification of structural market inefficiencies. 
*   We rely entirely on advanced quantitative statistics: Generalized Autoregressive Conditional Heteroskedasticity (GARCH) for volatility, Augmented Dickey-Fuller (ADF) tests for stationary mean-reversion, and Clayton Copula matrices for systemic tail-risk correlation modeling.
*   Every single trade is normalized to $1R$ (Initial Risk), and the system's survival is dictated by the System Quality Number (SQN).

### C. Comprehensive Operational Desk Management
The system must function as an institutional-grade professional trading terminal for the team. This includes:
*   Tracking exactly *which* user or *which* algorithm executed what trade.
*   Performance metrics broken down per trader/algorithm (Win Rate, $R$-Multiple distributions, Drawdown depth).
*   Forced, hard-coded risk limits (Value at Risk - VaR) that automatically sever API connections if human or algorithmic drawdowns exceed structural limits.

## 3. High-Level System Architecture (The "What")
To build this end-to-end proprietary quantitative solution, STOCKSTATS is divided into several highly decoupled microservices.

### I. The Data Ingestion Engine (The Eyes)
*   **Purpose:** To consume, mathematically scrub (via Hampel Filters), and permanently store massive amounts of real-time and historical market data (L1 trades, L2 order book depth) across multiple asset classes without relying on rate-limited retail APIs.
*   **Requirements:** Ultra-low latency WebSocket connections, high reliability, and a robust `TimescaleDB` PostgreSQL architecture capable of storing microsecond-level tick data. **Crucially, during Phase 1, the ingestion universe is strictly locked to a maximum of 50 assets** to guarantee computational stability and eliminate `HTTP 429` exchange bans.

### II. The Quantitative Logic Engine (The Mathematical Brain)
*   **Purpose:** The statistical core that processes incoming data arrays against our proprietary Linear Formulas (Kalman Filters, OLS regression, Cointegration).
*   **Requirements:** Capable of running complex matrix algebra computationally fast enough to generate localized signals. Completely devoid of human emotion. Must include a rigorous historical backtesting environment to prove mathematical expectancy while mathematically penalizing overfitting via the Deflated Sharpe Ratio (DSR).

### III. The Execution & Routing Engine (The Hands)
*   **Purpose:** To intercept the mathematically pure "Buy/Sell" signals from the Logic Engine, evaluate contextual liquidity toxicity, and physically route the capital to various exchanges with mathematically minimized slippage.
*   **Requirements:** Smart Order Routing (SOR), VWAP execution slicers, deterministic UUID State Machine reconciliation (`clientOid`), and fail-safes (Value at Risk Kill Switches).

### IV. The Machine Learning Overlay (The Filter)
*   **Purpose:** To act as the final Artificial Intelligence gatekeeper before capital is deployed.
*   **Requirements:** Ingests fractionally differenced stationary data. Analyzes Triple-Barrier labeled historical features using XGBoost or Random Forests to assign a dynamic Probability of Success to the linear mathematical signal. Vetoes the trade if the structural environment is deemed unconditionally hostile (aiming to maximize the F1-Score).

### V. The Internal Trading Desk Dashboard (The Command Center)
*   **Purpose:** A custom user interface and operational REST backend designed specifically for the internal human team to monitor the autonomous algorithms.
*   **Requirements:**
    *   **Authentication & Roles:** Admin (Full Kill Switch control), Trader (Parameter adjustments), Analyst (Read-only database access).
    *   **The Immutable Ledger:** A cryptographic log of every historical trade tagged with the responsible algorithm or human ID.
    *   **Performance Analytics:** Real-time dashboards tracking VaR, SQN, Expectancy, and current macro Regime states (HMM).
    *   **Manual Overrides:** The ability for authorized Admins to manually intervene and instantly liquidate algorithmic positions to cash during unforeseen Black Swan events.
