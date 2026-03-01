# The STOCKSTATS Roadmap: Pragmatic Evolution to Autonomy

## Objective
The ultimate objective of the STOCKSTATS project is to build a mathematically rigorous, fully autonomous algorithmic trading desk capable of deploying capital 24/7 across fragmented global liquidity pools.

We unconditionally recognize that autonomous trading carries extreme systemic and financial risk. Therefore, the system will *not* be built using a monolithic "Big Bang" deployment strategy. It will be constructed defensively in **9 distinct sequential phases**, prioritizing a Minimum Viable Edge (MVE) and robust data sterilization before any complex automation is permitted.

---

## Phase 1: The Ingestion Scrubber & Minimum Viable Edge (MVE)
Complex mathematical models will fail catastrophically if built on dirty data or if the exchange APIs rate-limit our connections. Phase 1 completely avoids UI development to focus entirely on gathering sterilized, point-in-time data.
*   **Action items:** 
    *   Deploy **TimescaleDB** for hyper-optimized tick storage.
    *   Prioritize the implementation of the **Numba Hampel Filter (Model 14)** to mathematically scrub "Rogue Ticks" before they can permanently poison the database.
    *   **The 50-Asset Universe Constraint:** Restrict all ingestion and logic processing strictly to a maximum of 50 assets. This mathematically prevents API rate-limit exhaustion and database I/O bottlenecks during the structural rollout.
    *   Build an explicit **API Rate Limit Manager (Token Bucket)** to autonomously throttle REST/WebSocket requests, legally protecting our IPs from exchange bans during high-volume array polling.
*   **Completion Criteria:** The isolated Python Ingestion Engine can stably ingest, scrub, and store L1 trades and L2 snapshots for 50 assets 24/7 without a single memory leak or API `HTTP 429` penalty.

## Phase 2: The Quantitative Logic Engine ($E(R) > 0$)
With mathematically sterile data flowing, we build the core "brain" to prove our statistical edge.
*   **Action items:**
    *   Code the baseline linear models (GARCH volatility, ADF Cointegration, OLS spread arrays).
    *   Implement structural overlays (Hidden Markov Models for macro regime detection).
    *   Build the Backtesting Engine utilizing the un-corrupted Phase 1 Point-in-Time data.
    *   **Forward-Test via Shadow Mode (Strategy 14):** Deploy the compiled models purely against simulated local capital, strictly enforcing the mathematical execution penalties (real-time order book slippage and network latency) to prove out-of-sample viability.
*   **Completion Criteria:** The system successfully identifies historical pricing anomalies and mathematically proves a baseline $Expectancy (R) > 0$ after simulated real-world friction.

## Phase 3: The Grafana Command Center & Manual Execution
To avoid the "Big Bang" trap of spending 100+ hours building a custom React UI before taking a live physical trade, we embrace gritty pragmatism. Because we are trading our own limited retirement capital, the system acts strictly as an early-warning radar; the human founder acts as the execution weapon to prevent runaway bot algorithms from blowing up our accounts.
*   **Action items:**
    *   Deploy **Grafana** natively on top of PostgreSQL/TimescaleDB. Use Grafana's built-in RBAC to instantly render real-time L1 ticks and GARCH bands for optical validation, serving as our Phase 1 Command Center.
    *   When the Logic Engine detects an anomaly, push a Tier 2 Webhook alert directly to Slack/Discord.
*   **Completion Criteria:** The founder receives a Discord alert, visually verifies the math purely via Grafana dashboards, logs into the physical broker, and successfully deploys a manual Fractional Kelly limit order (e.g., $\$400$ micro-slices). **Goal:** Prove the mathematical $R > 0$ edge with our own real capital and establish survival protocols before engineering complex Smart Order Routers.

## Phase 4: Risk Matrices & Capital Sizing (Defense Systems)
Before we let the machine trade autonomously, we must teach it how to mathematically protect the capital from "Fat Tail" events.
*   **Action items:**
    *   Implement the Copula dependency matrices to calculate cross-asset tail risk (Crash probabilities).
    *   Implement the Fractional Kelly Criterion ($0.5f^*$) to size each specific signal dynamically based on its Win Rate.
    *   Implement the Parametric Value at Risk (VaR) Master Kill Switch (Model 12) directly into the logic loop.
*   **Completion Criteria:** The system autonomously rejects signals that mandate capital allocations too large, too correlated, or that breach the daily $5\%$ portfolio drawdown limit.

## Phase 5: The Smart Order Router (Semi-Automation)
*The framework calculates sizes and routes the orders; the human clicks "Approve."* At this stage, we transition from the Grafana dashboard to the bespoke React Next.js Terminal.
*   **Action items:**
    *   Build the specialized `Next.js` Trading Desk Dashboard (Strategy 07).
    *   Build the Python execution integration with CCXT.
    *   Implement the VWAP Slicer to fraction large parent orders (The 5% Participation Rule).
    *   Implement Order Book Imbalance (OBI) toxicity sensors to prevent Adverse Selection.
*   **Completion Criteria:** The Next.js dashboard presents a tailored order ticket alongside the algorithmic signal. The human trader reviews it and visually clicks "Authorize Execution." The system autonomously slices and routes the order, systematically minimizing negative slippage. 

## Phase 6: Systemic Reconciliation & Ledger Parity
The "Zombie Order" defense framework.
*   **Action items:**
    *   Hardcode the cryptographic `clientOid` UUID protocol into all physical execution payloads.
    *   Build the rigid Order State Machine (Pending $\rightarrow$ Acknowledged $\rightarrow$ Partially_Filled).
    *   Implement the HTTP 504 Timeout Rescue Protocol (The API interrogator).
*   **Completion Criteria:** The system proves it can transparently survive a catastrophic exchange API outage or matching engine crash without accidentally double-spending or stranding deployed grid capital.

## Phase 7: Full Autonomy (The Machine Takes Control)
*The system assumes complete topological trading control on the local Basement Server; the human acts purely as a macro risk monitor.*
*   **Action items:**
    *   Sever the "Human Approval" UX friction from the Smart Order Router.
    *   Connect the Logic Engine directly to the Risk Engine and SOR via Kafka event buses.
    *   Deploy the 4 Dockerized microservices strictly within the isolated Production Docker Network on the Basement Server.
*   **Completion Criteria:** The system autonomously identifies an anomaly, verifies GARCH conditions, calculates Copula tail-risk, sizes via Fractional Kelly, checks OBI toxicity, and fully executes the VWAP slices—entirely without human intervention, 24/7/365.

## Phase 8: Machine Learning Overlays (Meta-Labeling)
The final stage of structural optimization. We do not use ML to generate foundational trades; we strictly use it to veto false positives.
*   **Action items:**
    *   Extract the "Ground Truth" manual execution ledger populated during Phase 3.
    *   Implement Fractional Differencing ($d \approx 0.45$) on all data arrays to achieve stationarity while preserving memory.
    *   Train an XGBoost algorithmic classifier using the Triple-Barrier Method.
    *   Inject the compiled ML model directly before the SOR as a final probability filter.
*   **Completion Criteria:** The Win Rate ($P_w$) and System Quality Number (SQN) actively increase due to Artificial Intelligence successfully vetoing losing mathematical trades mere milliseconds prior to L2 execution.

## Phase 9: Cloud Infrastructure Migration (Scaling & Latency Arbitrage)
Once the fully automated system has been running live in Production on the Basement Server for several months, proving its $E(R)>0$ expectancy across all market conditions without physical hardware bottlenecks, we execute the final structural pivot.
*   **Action items:**
    *   Migrate the TimescaleDB ledger securely to a managed cloud database (e.g., AWS RDS or Timescale Cloud).
    *   Deploy the Production Docker containers to a dedicated AWS Virtual Private Cloud (VPC) cluster (e.g., ECS or EKS).
    *   **The Geo-Location Optimization:** Co-locate the AWS VPS in the exact physical region of the centralized exchange (e.g., Tokyo `ap-northeast-1` for Binance) to drop execution latency to $< 5$ milliseconds.
*   **Completion Criteria:** The entire STOCKSTATS macro-architecture is 100% decommissioned from the residential Basement Server and operates globally on hardened, enterprise-grade external cloud infrastructure, achieving institutional latency reductions.
