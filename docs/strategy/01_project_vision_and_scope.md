# STOCKSTATS: Project Vision & Scope

## 1. Executive Summary
The **STOCKSTATS** system is a proprietary, internally-developed algorithmic quantitative trading platform designed exclusively for our team. It is strictly not a commercial Software-as-a-Service (SaaS) product. 

Its primary mathematical mandate is to execute purely quantitative trading strategies—specifically focusing on **Statistical Arbitrage (Pairs Trading)**, **Mean Reversion**, and **Intraday Volatility Profiling**—across global equities and cryptocurrency liquidity pools, ensuring a mathematically proven, positive expected value ($E(R) > 0$).

Crucially, the system is designed as a **comprehensive operational platform**, not just a trading script. It is being developed through a strictly phased architectural roadmap (see `00_roadmap.md`). It initially serves as a highly advanced manual signal terminal, maturing linearly into a fully autonomous, Machine-Learning-overlayed algorithmic engine. 

Throughout all phases, STOCKSTATS acts as the central hub for the proprietary trading desk: tracking individual quantitative researcher performance, enforcing unyielding portfolio risk limits, and providing a unified operations dashboard.

## 2. Core Operational Mandates

### A. The Proprietary Edge
The logic engine, mathematical models, and latency-sensitive execution algorithms are strictly internal. The infrastructure must be aggressively secure, self-hosted (or securely managed in isolated cloud VPCs), and built fundamentally to protect our algorithmic "edge." Third-party dependencies are minimized to prevent intellectual property leakage.

### B. Core Operational Directives
5.  **Latency is Guaranteed:** The architectural baseline is that the system will inevitably experience network vacuums (e.g., HTTP 504 timeouts). Logic cascades must mathematically self-reconcile without structural decay.
6.  **Shadow Mode is Mandatory:** Standard "Paper Trading" creates false expectations. The system must support a structural `SHADOW` mode that actively penalizes mock executions based on physical L2 liquidity depth and network latency to test new algorithms under realistic stress.

### C. The $E(R) > 0$ Intelligence Engine
The system does not guess. The absolute core of STOCKSTATS is the automated mathematical identification of structural market inefficiencies. 
*   We rely entirely on advanced quantitative statistics: Generalized Autoregressive Conditional Heteroskedasticity (GARCH) for volatility, Augmented Dickey-Fuller (ADF) tests for stationary mean-reversion, and Clayton Copula matrices for systemic tail-risk correlation modeling.
*   Every single trade is normalized to $1R$ (Initial Risk), and the system's survival is dictated by the System Quality Number (SQN).

### D. Comprehensive Operational Desk Management
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

## 4. A Day in the Life of the Engine (System Lifecycle)

For a developer or a quant standing back and looking at the repository, it can be difficult to conceptualize how all the fragmented mathematical models and microservices interact continuously in reality. This section strips away the code and explains exactly how the system breathes, moves, and defends capital on a minute-by-minute basis. We break this down into two perspectives: **Under the Hood** (what the Docker microservices are doing) and **Over the Hood** (what the human operator experiences).

### A. A Minute in the Life (The Continuous Loop)
The system does not sleep. It operates on a continuous, high-frequency, asynchronous loop. Here is exactly what happens during a standard 60-second window while the market is "normal" (no active trades).

**⚙️ Under the Hood (The Microservices)**
1. **The Ingestor Breathes (Milliseconds):** The `Python CCXT Gateway` container is connected to the exchange WebSocket. Every 50 milliseconds, a new physical trade occurs. The WebSocket pushes this tick down the pipe.
2. **The Scrubber Vetoes (Microseconds):** Before the tick is saved, the Python engine routes the price through the **[Numba Hampel Filter (Model 14)](../models/14_data_scrubbing_hampel.md)**. If the exchange glitches and sends a rogue physical price, the filter instantly detects the statistical anomaly and silently drops the tick.
3. **The Dual-Write (Milliseconds):** The sterile tick is simultaneously written to the permanent **TimescaleDB** ledger and pushed into the ephemeral **Redis** cache.
4. **The Math Engine Wakes Up (Seconds):** Every 10 seconds, the `Quantitative Logic` container wakes up. It asks Redis for the last 500 clean ticks. It runs the **[GARCH(1,1) Volatility Index (Model 01)](../models/01_garch_volatility.md)** to check for market shocks, and the **[Cointegration ADF Test (Model 02)](../models/02_cointegration_arb.md)** to see if the mathematical spread has widened.
5. **The AI stands by:** Because the spread has *not* widened, the Expected Value $E(R)$ is $\le 0$. The Math engine goes back to sleep.

**👁️ Over the Hood (The Operator)**
1. **The Human is Passive:** The proprietary Next.js Command Terminal is open. 
2. **The Radar Sweeps:** The TradingView charts hit the `Next.js API` every 5 seconds, fetching the latest GARCH bands and rendering them instantly via WebGL. 
3. **System Status:** A small green light in the corner confirms the Docker container is healthy. The human does nothing.

### B. An Hour in the Life (The Attack & The Execution)
Suddenly, a massive institutional seller dumps 1,000 BTC. The architecture violently shifts from passive surveillance to active mathematical engagement.

**⚙️ Under the Hood (The Microservices)**
1. **The Spread Violates the Boundary:** The Math Engine wakes up. The **Cointegration Model** screams: The spread has violently stretched to $3.5$ Standard Deviations ($E(R) > 0$).
2. **The XGBoost Veto ([Model 10](../models/10_machine_learning_overlays.md)):** The Math engine silently passes the state to the **Machine Learning Classifier**. The AI compares this dump to historical training data. The AI returns a probability: `0.85 (Clear to Engage)`. The veto is bypassed.
3. **The Risk Matrix Computes ([Model 06](../models/06_copula_kelly_sizing.md)):** The **Value at Risk (VaR)** engine and **Clayton Copula Matrix** check for systemic contagion. The **Fractional Kelly Formula ($f^*$)** dictates the exact position size to risk.
4. **The Smart Order Router ([Model 04](../models/04_vwap_liquidity.md)):** The Router splits the large parent order into 50 micro-orders to prevent slippage.
5. **The Order Book Imbalance ([Model 15](../models/15_orderbook_toxicity_obi.md)):** The Router checks the Redis L2 cache. The `Ask` side is toxic (spoofed sell walls). The Router pauses for $800$ milliseconds, waits for the toxicity to clear, and fires cryptographically signed limit orders.

**👁️ Over the Hood (The Operator)**
1. **The UI Flashes:** The Next.js dashboard flashes a yellow warning: `[SIGNAL GENERATED: COINTEGRATION SPREAD]`.
2. **The ML Probability Shows:** The UI displays the AI's confidence score (`85%`) and the Kelly position size.
3. **The Webhook Fires:** A Discord/Slack webhook silently buzzes the Operator's phone: `EXECUTION INITIATED: Splitting VWAP`.
4. **The Human is Passive:** The human watches the UI as the Smart Order Router visually ticks down to hide from institutional radars.

### C. A Day in the Life (The Defense & The Exit)
The position is open. The algorithm must now defend the capital and orchestrate the mathematical exit.

**⚙️ Under the Hood (The Microservices)**
1. **The Kalman Filter Tracks ([Model 07](../models/07_kalman_filters.md)):** The market moves in our favor. The **Kalman Filter** dynamically adjusts the "true" Hedge Ratio of the trade tick-by-tick.
2. **The State Machine Reconciles ([Model 13](../models/13_state_machine_reconciliation.md)):** Suddenly, the Exchange API crashes. The system receives an `HTTP 504 Gateway Timeout`. Our **State Machine** intercepts the 504 using a deterministic UUID (`clientOid`), safely pauses, and queries the exchange later: *"Did my specific order fill before you crashed?"*, structurally preventing a Double-Spend.
3. **The Exit:** The spread fully mean-reverts ($E(R) \le 0$). The Router slices the exit order and closes the trade.
4. **The Ledger Locks ([Strategy 11](11_database_schema_and_ledgers.md)):** The PnL is aggressively written to `immutable_execution_ledger` in TimescaleDB. A PostgreSQL trigger physically locks the row from tampering.

**👁️ Over the Hood (The Operator)**
1. **The Daily Audit:** It is 11:00 PM. The human logs into the Command Terminal. 
2. **The System Quality Number ([Model 05](../models/05_expectancy_and_sqn.md)):** The UI displays the day's PnL and the **SQN**. The Operator mathematically verifies *how much risk* was required to make that money, proving the system is maintaining statistical dominance.
3. **Zero Maintenance:** The Docker orchestrator has kept the RAM strictly below the OOM threshold. The system runs seamlessly into the night.

### D. Summary of the Paradigm
* The **Human** validates the mathematics and monitors the telemetry.
* The **Docker Microservices** protect the physical server.
* The **CCXT Gateway** and **TimescaleDB** act as the sterile heart pumping data.
* The **Math Engine** and **XGBoost ML** act as the sniper, waiting patiently for overwhelming statistical superiority before deploying the **Fractional Kelly** bullet.
