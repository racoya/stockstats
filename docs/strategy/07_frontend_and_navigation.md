# Strategy 07: Frontend & Navigation Architecture

## 1. The Operational Objective
To strictly define the frontend architecture, routing logic, and systemic error handling mechanisms for the proprietary Trading Desk Dashboard. The UI must ensure entirely seamless execution navigation while enforcing mathematically rigid security cordons across different Role-Based Access Control (RBAC) tiers.

Because the system manages extremely high-velocity capital deployment, the UI cannot be built like a standard React web-app. It must be built as a high-frequency, dark-mode terminal.

## 2. Dynamic 404 Routing & Contextual Security
Based on the explicit architectural mandate for secure internal tools, a unified 404 (Not Found) or 403 (Unauthorized) HTTP response is a severe operational hazard. The system must degrade gracefully and contextually based on the active user's role.

*   **The Hazard:** Generic 404 pages leak system structures to unauthorized Analysts or trap Execution Traders in navigational dead-ends during fast-moving $+3\sigma$ market volatility constraints.
*   **The Solution (Contextual Error Boundaries):**
    *   **Administrator 404:** Displays the specific routing exception but injects immediate quick-action modules linking to backend PostgreSQL diagnostics, Node.js server error logs, and the **[Master Kill Switch]**. They receive a prominent path to the **[VaR Parameters]** module to ensure global limits aren't breached while they debug the routing error.
    *   **Execution Trader 404:** A stripped-down, high-contrast error message that suppresses technical diagnostics. It provides a massive, instantaneous "Return to **[Command Center]**" or "**[Active Executions]**" button, structurally minimizing seconds lost during an active VWAP slice deployment.
    *   **Data Analyst 404:** Redacts all execution nomenclature. Instantly redirects or offers links back to the primary read-only dashboard or the `TimescaleDB` historical research interfaces.
*   **Security Posture:** Unauthorized access attempts (e.g., a Trader attempting to `GET /admin/api-keys`) masquerade flawlessly as a 404. It will not reveal whether a specific Admin endpoint physically exists, adhering strictly to "security through obscurity" best practices for internal financial tools.

## 3. RBAC Route Protection Architecture
The React/Next.js frontend enforces structural RBAC natively at the router level. This operates independently but entirely in tandem with the backend JWT validation loop.

*   **Higher-Level Route Cordons:** Domains like `/admin/models` or `/admin/users` are strictly cordoned off at the Next.js `middleware.ts` level. Unauthorized rendering is computationally intercepted *before* the DOM paints.
*   **Dynamic Sidebar Rendering:** The global navigation framework actively parses the user's encrypted JWT token payload (`Role: Analyst`). It physically removes execution hyperlinks from the DOM, ensuring an Analyst cannot even click a route that leads to a manual VWAP deployment module.

## 4. User Experience (UX) & Module Layout
The UI prioritizes execution speed, quantitative data density, and infallible action-taking during high-stress market crashes.

### A. The Global Topography
*   **Persistent Top Bar (The HUD):** Displays the consolidated Top-Level metrics: Aggregate Portfolio Net Asset Value (NAV), Daily $R$-Multiple generated, global API WebSocket status (Green/Amber/Red), and the structural "Halt All Executions" panic button (visible to Admins only).
*   **Collapsible Left Sidebar:** Dynamic routing heavily restricted by RBAC. Contains the primary domain toggles: 
    *   `[Execution Terminal]` (Live Trading)
    *   `[Portfolio & Systemic Risk]` (VaR & Copulas)
    *   `[Quantitative Analytics]` (Backtesting & SQN)

### B. Core Module: The Execution Terminal
This is the primary operational screen for the `Execution Trader` role. It must prevent cognitive overload while presenting all mandatory telemetry to authorize a Phase 3 systemic signal.
*   **Left Column (The Signal Vector):** A clean panel displaying the raw JSON payload from the Quantitative Engine. It explicitly highlights the Asset (`BTC_USD`), the Direction (`SHORT`), the Target Initial Risk (`1R = $150`), and the Expected Value (`E(R) = +2.5R`).
*   **Center Column (The Mathematical Proof):** A deeply integrated hyper-fast charting library (e.g., Lightweight Charts). It plots the real-time Level 1 Ticks overlaid perfectly with the live *GARCH(1,1) $+2\sigma$ bands* and *OLS regression trajectory*. This provides the human trader instantaneous visual proof of the mathematical anomaly.
*   **Right Column (The Order Matrix):** The authorization ticket, algorithmically pre-filled. The user views the expected L2 slippage, confirms the Fractional Kelly position size ($0.5f^*$), and clicks the prominent **[Deploy VWAP Router]** button.

### C. Core Module: Portfolio Risk & Exposure
This is the macro screen for `Admins` monitoring the health of the logic clusters.
*   **The Copula Heatmap:** A visual array mapping current exposure across all active assets. If the Copula models detect extreme tail-risk dependency (e.g., BTC and ETH are $90\%$ likely to crash together), the respective sector blocks flash Amber to warn of clustered systemic risk.
*   **The VaR Drawdown Gauge:** A dominant visual dial tracking the rolling portfolio drawdown strictly against the Parametric Model 12 VaR limit. As the portfolio mechanically approaches the automated Kill Switch threshold, the UI elements escalate from Green $\rightarrow$ Amber $\rightarrow$ Flashing Red.

### D. UX Interaction Axioms
*   **The Zero-Polling Mandate:** Users must *never* be required to click "Refresh." All asset prices, SQN metrics, active order states (`ACKNOWLEDGED`), and OBI toxicity alerts must push instantly to the DOM via Server-Sent Events (SSE) or WebSockets.
*   **Destructive Action Friction:** Any financially destructive action (e.g., manually liquidating a $\$100k$ position or overriding an XGBoost Meta-Labeling veto) mathematically requires a secondary confirmation modal. The UI must explicitly state the quantifiable dollar-impact of the intervention before execution is authorized.
