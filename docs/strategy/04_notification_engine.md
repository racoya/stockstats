# Strategy 04: The Notification Engine & System Comm

## 1. Objective
To design an ultra-low-latency, multi-channel notification architecture that instantly broadcasts system state changes, quantitative model signal generation, and critical mathematical risk events to the appropriate human operators based on their Role-Based Access Control (RBAC) levels.

The system cannot rely purely on the Operations Dashboard UI for alerts. It must actively "push" telemetry to the team through heavily redundant external channels.

## 2. Notification Urgency Hierarchy (The Tiers)
Alerts are not created equal. A routine end-of-day regression log must not trigger the same physical response as an instantaneous Value at Risk (VaR) portfolio breach.

### Tier 1: CRITICAL (Immediate Human Intervention Required)
*   **Trigger Events:** 
    *   The Parametric VaR (Model 12) Master Kill Switch is triggered.
    *   The `clientOid` State Machine (Model 13) encounters 3 sequential REST API timeouts (Exchange Failure).
    *   A massive, unforeseen Correlated Drawdown triggers the Copula Safety Veto.
    *   The database encounters a Write-Ahead Log (WAL) failure causing local ledger de-sync.
*   **Broadcast Channels:** SMS / Automated SIP Phone Call (e.g., via Twilio).
*   **Allowed Recipients:** Admins and Senior Quants only.
*   **Latency SLA:** $< 3.0$ seconds from system threshold breach to physical phone ring.

### Tier 2: HIGH (Algorithmic Action / Veto Overrides)
*   **Trigger Events:** 
    *   The Mathematical Model generates a valid $E(R)>0$ entry setup (GARCH & Cointegration checks pass).
    *   In Phase 3 (Human-in-the-Loop), the Smart Order Router requests explicit human permission to begin VWAP slicing.
    *   The XGBoost Meta-Labeling engine (Model 10) vetoes a mathematically sound trade due to high False-Positive probability, logging the veto for human review.
*   **Broadcast Channels:** Dedicated Slack/Discord/Telegram webhook channels, mapped closely to persistent visual/audio alerts on the Frontend Trading Desk Dashboard.
*   **Allowed Recipients:** All authorized, on-duty Trading personnel.

### Tier 3: ROUTINE (Telemetry & Health Diagnostics)
*   **Trigger Events:** 
    *   Daily Deflated Sharpe Ratio (DSR) recalibrations.
    *   HMM Regime Detection (Model 03) shifting from "State 0: Choppy" to "State 1: Trending".
    *   Routine API key rotation health checks.
    *   Hampel Filter (Model 14) scrubbing metrics (e.g., "12 rogue ticks scrubbed in the last 24h").
*   **Broadcast Channels:** Email / Internal Log Aggregation Dashboards (Grafana/Kibana) / A standard Daily End-of-Day Briefing channel.
*   **Allowed Recipients:** All user roles (Admin, Trader, Analyst).

## 3. Webhook & WebSocket Architecture
To guarantee the Frontend Trading Desk UI is perfectly synchronized with the PostgreSQL database *without* overwhelming the backend with inefficient HTTP polling loops:

*   **Server-Sent Events (SSE) / WebSockets:** The core logic engine physically broadcasts real-time state changes (`ACKNOWLEDGED` $\rightarrow$ `PARTIALLY_FILLED`) strictly via WebSockets directly to the authorized JSON web clients. This ensures the frontend portfolio VaR view is identical to the backend reality.
*   **The Webhook Router:** The system utilizes an internal event-driven queue (e.g., Redis Pub/Sub) to isolate signal generation from payload delivery. If the system generates an execution signal, it pushes it to the pub/sub queue. The autonomous Webhook Service consumes the event and formats the JSON payload for third-party REST APIs (Twilio, Discord) without blocking the primary quantitative processing loops.

## 4. Signal Alert Formatting (Standardized JSON)
Every Tier 2 trade signal broadcast to human operators (e.g., via Slack) must be strictly formatted. It must be instantly mathematically readable during fast-moving markets:

```yaml
[⚙️ TIER 2: SYSTEM ACTION]
Time (UTC): 09:41:02.145
Action: VWAP EXECUTION PAUSE
Strategy: Cointegration_Arb_BTC_ETH
Asset: BTC/USD
Side: LONG
Current_OBI_Toxicity: -0.84 (Highly Toxic)
VPIN_Flow: 88% Maker-Seller
Status: Holding 4 VWAP Slices ($40k). Awaiting L2 Book Normalization.

Click to Override & Force Execution: [Secure Dashboard UUID Link]
```

```yaml
[✅ TIER 2: SIGNAL GENERATION]
Time (UTC): 14:12:08.000
Strategy: GARCH_Mean_Reversion
Asset: SOL/USD
Side: SHORT
Entry_Zone: $148.50 - $149.00
Stop_Loss_1R: $152.00
Target_Take_Profit: $138.00 (+2.85R Expectancy)
XGBoost_Veto_Probability: 14% (SAFE)

Click to Approve Smart Order Router: [Secure Dashboard UUID Link]
```

## 5. Security & Redundancy Mechanics
*   **Encrypted Secrets:** All external Notification API keys (Twilio, Slack bots) must be encrypted at rest and injected strictly via memory environment variables (`.env`).
*   **Cascade Fail-Overs:** The webhook router must gracefully handle HTTP 429 Rate Limits from external providers. If Twilio rate limits the system during a flash crash due to too many alerts, the system automatically escalates the payload directly to the secondary encrypted Telegram channel.
