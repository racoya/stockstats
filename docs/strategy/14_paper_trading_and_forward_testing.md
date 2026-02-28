# Strategy 14: Shadow Mode (Institutional Paper Trading)

## 1. The Operational Objective
Standard "Paper Trading" offered by retail exchanges is fundamentally flawed. It executes mock orders at the exact Mid-Price without accounting for Order Book (L2) depth, creating a mathematically impossible "perfect" equity curve.

**STOCKSTATS requires an institutional-grade "Shadow Mode."** This mode must physically execute the entire algorithmic lifecycle (Ingestion, GARCH math, Copula Risk, VWAP Slicing) against *live* market data, but rather than sending signed REST payloads to the exchange, it diverts the final execution command to a local mocked State Machine that structurally calculates realistic execution penalties (Slippage and Taker Fees).

## 2. The Sandbox Architecture

### A. The Environment Variable Toggle
The difference between live capital destruction and safe Shadow Mode testing is governed strictly by a single global environment variable in the `.env` file of the Execution Router microservice:
`STOCKSTATS_EXECUTION_MODE="SHADOW"`

### B. The Diverted Execution Loop
When the VWAP Slicer (Model 04) authorizes a $\$5k$ micro-order to fire:
1.  **Check Execution State:** The Python API reads the `.env` variable.
2.  **Live Mode (`"LIVE"`):** The payload is cryptographically signed using CCXT and physically `POST`ed to the Binance API.
3.  **Shadow Mode (`"SHADOW"`):** The cryptographic signing is bypassed. The payload is handed to the `ShadowExecutionEngine` class locally.

## 3. The Mathematics of Realistic Simulation

To train the engineering team and prove the $E(R)>0$ edge (Model 05) out-of-sample, Shadow Mode must aggressively penalize theoretical executions to match physical reality.

### A. The Slippage Penalty Matrix
If the algorithm signals a Buy at exactly $\$50,000.00$, Shadow Mode will **never** log a fill at $\$50,000.00$. 
The `ShadowExecutionEngine` must poll the local Redis L2 Order Book (Model 15).
*   **Action:** It literally "walks the book." It calculates how deep into the Ask side of the L2 array a physical $\$5k$ market order would chew before being completely filled. 
*   **Result:** It returns a mathematically realistic Volume-Weighted Fill Price (e.g., $\$50,003.50$).

### B. The Latency Delay
API network transit time (Heartbeat Latency) is a structural risk.
*   **Action:** When a Shadow Order is generated, the system physically `asyncio.sleep()`s for the exact millisecond duration of the last recorded websocket ping (e.g., 42ms) before attempting the fill.
*   **Result:** If the L1 price materially moves during those 42 milliseconds, the Shadow Fill mathematically slips further away.

### C. The Friction Matrix (Fees)
Shadow Mode must unconditionally deduct the exact Maker/Taker fee tier of the targeted exchange upon every mock execution.
*   **Example:** Binance charges $0.04\%$ Taker. For a simulated $\$100,000$ round-trip trade, the Shadow Engine immediately deducts $\$80$ from the simulated Capital Balance.

## 4. UI/UX Integration (The Training Dashboard)

To effectively train operators and operators, the Next.js Operation Dashboard must natively support Shadow Mode visualization.

### A. The Visual Warning Banner
When `STOCKSTATS_EXECUTION_MODE="SHADOW"`, the Navbar must physically pulse a high-visibility warning (e.g., striped amber/black) reading: **"⚠️ SHADOW MODE - CAPITAL PROTECTED"**.

### B. Separated Databases
Simulated executions cannot pollute the `immutable_execution_ledger` used for tax reporting and XGBoost ground-truth labeling.
*   **Solution:** All Shadow Executions are diverted by the PostgreSQL trigger into a dedicated `shadow_execution_ledger` table.

## 5. Deployment Use Cases

1.  **Unit Testing (CI/CD):** The GitHub Actions pipeline runs Shadow Mode against massive arrays of historical flat-files to verify logic.
2.  **Engineering Training:** New Quants deploy untested mathematical models to Shadow Mode on their local docker clusters safely pulling live WebSocket data.
3.  **Forward-Testing (The Incubator):** Before a new algorithm (e.g., Cointegration Pair #42) is given live capital limits, it must run uninterrupted in Shadow Mode for 14 days and prove its out-of-sample Risk-Adjusted Expectancy (SQN $> 1.5$) under realistic slippage conditions.
