# Strategy 12: The Execution Sprints & Ticket Pipeline

This document serves as the master blueprint for transitioning STOCKSTATS from theoretical architecture into physical code. It mathematically maps the 8-Phase Roadmap (`00_roadmap.md`) into 28 strict, granular execution tickets.

This document must act as the primary local checklist during the entire engineering phase. **No tickets can be skipped or reordered without explicit authorization**, as deep dependencies exist between the PostgreSQL schemas and the Python mathematical integrations.

---

## Sprint 1: The Ingestion Scrubber & MVE
*The Minimum Viable Edge. Zero UI development. Establish the physically isolated database layer and begin feeding sterilized live crypto pricing arrays into TimescaleDB.*

- [ ] **Ticket 1.1: Stand up TimescaleDB and Redis Docker Containers**
  - **Priority:** High
  - **Action:** Scaffold the `docker-compose.yml` orchestrator. Pull official `timescale/timescaledb:latest-pg15` and `redis:alpine` images. Configure `.env` authentication.
- [ ] **Ticket 1.2: Execute SQL DDL Migrations (Strategy 11)**
  - **Priority:** High
  - **Action:** Write and execute the structured Data Definition Language into the physical TimescaleDB node, officially initializing the `l1_tick_history` hypertable using immutable `DECIMAL(24,8)` datatypes.
- [ ] **Ticket 1.3: Build Python Base & Rate Limiter (Token Bucket)**
  - **Priority:** High
  - **Action:** Scaffold the `backend/ingestion/` Python microservice. Install `asyncio`, `ccxt`, `asyncpg`, and `numba`. Explicitly build the `RateLimiterTokenBucket` class to throttle REST/WebSocket requests.
- [ ] **Ticket 1.4: Build CCXT Async WebSocket Ingestor (Max: 50 Assets)**
  - **Priority:** High
  - **Action:** Build the async ingestion loops targeting Binance/Kraken. Hardcode the target `Asset_Universe` array strictly to a maximum of 50 high-volume tickers to prevent `HTTP 429` exchange bans.
- [ ] **Ticket 1.5: Implement Numba Hampel Filter (Model 14)**
  - **Priority:** High
  - **Action:** Compile the advanced Median Absolute Deviation (MAD) array loop using `@njit` from Numba. Overwrite outliers explicitly before passing the batch list to `asyncpg` for disk insertion.

---

## Sprint 2: The Quantitative Logic Engine ($E(R)>0$)
*With sterile ticks flowing into the database, construct the mathematical core. Prove the statistical edge.*

- [ ] **Ticket 2.1: GARCH(1,1) Volatility Arrays (Model 01)**
  - **Priority:** High
  - **Action:** Implement rolling 500-period variance matrices ($\sigma^2$) directly against the incoming L1 ticks, feeding the dynamic bands into Redis.
- [ ] **Ticket 2.2: Johansen Cointegration Tests (Model 02)**
  - **Priority:** High
  - **Action:** Implement the statistical arbitrage engine, actively calculating the stationary Z-Score spreads between the synthetic asset pairs in the 50-asset universe.
- [ ] **Ticket 2.3: Hidden Markov Macro Regimes (Model 03)**
  - **Priority:** Medium
  - **Action:** Implement the structural state overlays (State 0: Choppy/Mean Reverting vs State 1: Trending) using the Python `hmmlearn` module.
- [ ] **Ticket 2.4: Kalman Filter Hedge Ratios (Model 07)**
  - **Priority:** Medium
  - **Action:** Implement dynamic beta tracking over the Cointegration pairs to mathematically prevent static hedge ratio decay.
- [ ] **Ticket 2.5: Point-in-Time Backtesting Engine (Model 11)**
  - **Priority:** High
  - **Action:** Build the historical `Pandas` scanner that queries the TimescaleDB hypertable to officially prove $E(R)>0$ while actively penalizing curve-fitting via the Deflated Sharpe Ratio (DSR).

---

## Sprint 3: Grafana Command Center & Manual Trading
*Phase 1 "Human-in-the-Loop" execution. Bypass Next.js to immediately deploy capital and gather ML Ground Truth labels.*

- [ ] **Ticket 3.1: Stand up Grafana via PostgreSQL Connector**
  - **Priority:** High
  - **Action:** Deploy a local `grafana/grafana-enterprise` container. Configure it to query the TimescaleDB ledger securely. Build the central view mapping L1 price vectors directly against the GARCH variance lines.
- [ ] **Ticket 3.2: Configure Slack/Discord Tier 2 Webhooks**
  - **Priority:** Medium
  - **Action:** Implement the Notification Engine (Model 04). Connect the Python Logic Engine to the designated Slack API channel to physically alert the trading desk when a mathematical anomaly is detected.
- [ ] **Ticket 3.3: First Live Capital Deployment (Manual Testing)**
  - **Priority:** High
  - **Action:** The human operator visually verifies a webhook signal in Grafana, routes a manual Maker Limit order on Binance, and physically logs the resulting execution via the DB terminal to create the very first "Ground Truth" Machine Learning row.

---

## Sprint 4: Risk Matrices & Capital Sizing (Defense Systems)
*Protecting the proven $E(R)>0$ edge from "Fat Tail" systemic shocks.*

- [ ] **Ticket 4.1: Clayton Copula Tail-Risk Matrices (Model 06)**
  - **Priority:** High
  - **Action:** Implement dependency mapping across the 50-asset universe to proactively detect systemic crash clustering *before* the execute command is issued.
- [ ] **Ticket 4.2: Fractional Kelly Optimization (Model 06)**
  - **Priority:** High
  - **Action:** Implement the dynamic $f^*$ position sizing methodology, scaling the specific trade volume mathematically based purely on the specific algorithm's historical Win Rate.
- [ ] **Ticket 4.3: Value at Risk (VaR) Kill Switch (Model 12)**
  - **Priority:** High
  - **Action:** Implement the Parametric VaR logic to instantly sever API exchange connections if localized rolling portfolio drawdowns physically breach $5\%$.

---

## Sprint 5: The Smart Order Router / Next.js Terminal
*Beginning the transition to automation. Build the proprietary Web Application.*

- [ ] **Ticket 5.1: Next.js Terminal UI Boilerplate**
  - **Priority:** Medium
  - **Action:** Scaffold the React 18 / TypeScript Operations Dashboard. Initialize the Tailwind aesthetics and integrate the exact Role-Based 404 security routing architecture (Admin, Trader, Analyst).
- [ ] **Ticket 5.2: CCXT Execution Routing API**
  - **Priority:** High
  - **Action:** Build the `backend/execution/` Python service. Define the endpoints capable of securely generating and signing cryptographic `POST /api/v3/order` payloads targeting the brokerage API.
- [ ] **Ticket 5.3: Order Book Imbalance (OBI) Sensor (Model 15)**
  - **Priority:** High
  - **Action:** Build the real-time toxicity dial in the UI. Ensure it successfully reads localized L2 JSON arrays from the Redis bucket to actively veto incoming trades attempting to execute into hostile HFT spoofing.
- [ ] **Ticket 5.4: VWAP Execution Slicer (Model 04)**
  - **Priority:** High
  - **Action:** Build the mathematical Time-Weighted and Volume-Weighted slicing protocols. The algorithm must automatically dissect a $\$100k$ parent block into $\$5k$ micro-orders to hide intentions from the L2 order book.
- [ ] **Ticket 5.5: Build Shadow Execution Simulator (Strategy 14)**
  - **Priority:** High
  - **Action:** Implement the `ShadowExecutionEngine` class in Python. It must actively bypass CCXT, poll the local Redis L2 book to calculate mock slippage volume, delay the logic via network ping values, and execute the mock trade purely against the `shadow_execution_ledger` table.

---

## Sprint 6: Systemic Ledger Reconciliation (The Zombie Order Defense)
*Guaranteeing that internal database arrays perfectly match external exchange matching-engine arrays.*

- [ ] **Ticket 6.1: Deterministic `clientOid` UUID protocol**
  - **Priority:** High
  - **Action:** Hardcode the cryptographic UUID tracking tags natively into all parent and child VWAP order requests to ensure 1:1 tracking capability across network hops.
- [ ] **Ticket 6.2: Execution State Machine (Model 13)**
  - **Priority:** High
  - **Action:** Build the strict `Pending -> Acknowledged -> Filled/Rejected` lifecycle monitor across the database architectures to definitively detect and track orphaned VWAP grid orders.
- [ ] **Ticket 6.3: HTTP 504 Timeout Rescue Protocol**
  - **Priority:** High
  - **Action:** Build the automatic API "Interrogator" loop to aggressively ping the exchange via `GET /order/status` to determine true physical execution status during network-level flash crashes.

---

## Sprint 7: Full Autonomy (Local Basement Server)
*Severing the human approval UX friction. The algorithm takes exclusive control 24/7 on the local machine.*

- [ ] **Ticket 7.1: Kafka/Redis PubSub Event Buses**
  - **Priority:** High
  - **Action:** Refactor the architecture to deeply decouple the Python Logic Engine from the separate Risk Engine. Connect them via high-frequency message brokers to guarantee topological fault tolerance.
- [ ] **Ticket 7.2: Decouple Frontend Execution UX Friction**
  - **Priority:** Medium
  - **Action:** Physically remove the React "Confirm Open Route" buttons from the UI terminal, officially converting the Next.js application into a passive, read-only monitoring dashboard.
- [ ] **Ticket 7.3: Local Docker Production Deployment**
  - **Priority:** High
  - **Action:** Transition the 4 architectural components into their formal `stockstats-prod` headless Docker configurations, routing all communication entirely over the isolated internal port network (e.g., `localhost:5434`).

---

## Sprint 8: XGBoost Machine Learning Overlays (Meta-Labeling)
*The final mathematical optimization. Injecting Artificial Intelligence strictly to veto linear false-positives.*

- [ ] **Ticket 8.1: Fractional Differencing Arrays (Model 09)**
  - **Priority:** High
  - **Action:** Transform non-stationary price curves into mean-reverting memory proxies ($d \approx 0.45$) specifically to prepare the input features for the XGBoost gradient boosting decision matrices.
- [ ] **Ticket 8.2: Extract Phase 3 Manual Ground Truth Labels**
  - **Priority:** High
  - **Action:** Interrogate the `immutable_execution_ledger` for the historical Slippage Deltas (Algorithm Intent vs. Human Final Reality) gathered manually throughout Sprint 3.
- [ ] **Ticket 8.3: Train XGBoost Classifier (Model 10)**
  - **Priority:** High
  - **Action:** Use the Triple Barrier Method over fractional features to physically train the ML gradient booster to detect False Positive linear mathematical signals on out-of-sample data.
- [ ] **Ticket 8.4: Inject ML Veto into Smart Order Router**
  - **Priority:** High
  - **Action:** Hardcode the constraint requiring the $E(R)>0$ math signal to execute through the fast-compiled XGBoost probability tree *before* the VWAP Slicer deploys. A veto requires an instant algorithmic stand-down.

---

## Sprint 9: Cloud VPC Migration (AWS Optimization)
*The final infrastructure pivot. Executed only after months of proven, profitable automation on the local Basement Server.*

- [ ] **Ticket 9.1: Provision AWS Tokyo VPS & RDS**
  - **Priority:** Medium
  - **Action:** Deploy the physical AWS EC2 compute instances (`ap-northeast-1`) and configure the heavily restricted internal Virtual Private Cloud (VPC) firewalls.
- [ ] **Ticket 9.2: TimescaleDB Migration & Ledger Sync**
  - **Priority:** High
  - **Action:** Safely execute a continuous WAL replication or logical dump from the Basement Server to the AWS Cloud Ledger without losing a single L1 tick or execution state.
- [ ] **Ticket 9.3: Cutover & Latency Validation**
  - **Priority:** High
  - **Action:** Gracefully shut down the Basement Docker execution routers, deploy the Docker images to the AWS ECS cluster, and mathematically verify the drop in L2 Execution network latency from $\sim40$ms domestic to $<5$ms co-located.
