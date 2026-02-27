# Frontend & Navigation Strategy

## 1. Objective
To define the frontend architecture, routing logic, and error handling mechanisms for the Trading Desk Dashboard, ensuring seamless navigation and strict security across different user roles.

## 2. Role-Based Access Control (RBAC) Architecture
The frontend will implement a strict RBAC system to ensure users only see and interact with components they are authorized to access. This operates independently but in tandem with backend API validation.

*   **Admin Route Protection:** Higher-level routes (e.g., `/admin/kill-switches`, `/admin/users`) are cordoned off at the routing level. Unauthorized access attempts will be intercepted before rendering.
*   **Dynamic Navigation Menus:** The main sidebar/navigation bar will dynamically render links based on the user's JWT token payload (or active session role). Analysts will not even see the link to manual execution modules.

## 3. Dynamic 404 Error Pages & Exception Handling
Based on industry standards for secure internal tools, a unified 404 (Not Found) or 403 (Unauthorized) response is insufficient. The system must degrade gracefully and contextually.

*   **The Problem:** Generic 404 pages can leak system structure to unauthorized users or trap users in dead-ends during fast-moving market events.
*   **The Solution - Contextual Error Boundaries (Updated for Phase 7 Layout):**
    *   **Admin 404 (Head Trader / Risk Mgr):** Displays the error but provides quick-action links to system diagnostics, recent backend error logs, and the **[Execution Ledger]**. They also receive a prominent link to the **[Risk Parameters]** module to ensure global VaR limits aren't breached.
    *   **Trader 404:** Streamlined error message that immediately provides a prominent "Return to **[Command Center]**" or "**[Cointegration Matrices]**" button, minimizing time lost during active trading sessions.
    *   **Analyst/Viewer 404:** Redirects or offers links back to the primary **[Command Center]** read-only dashboard or historical data querying interfaces.
*   **Security Posture:** Unauthorized access attempts (403 masquerading as 404) will not reveal whether a specific Admin URL truly exists, adhering to "security through obscurity" best practices for internal tools. As we add new Next.js routes, this 404 boundary component will dynamically update its suggested links based on the user's validated Prisma `UserRole`.

## 4. User Experience (UX) & Interface Layout
The UI must prioritize speed, data density, and infallible action-taking during high-stress market environments. The design language will be dark-mode native (to reduce eye strain) with highly contrasting typography.

### A. The Global Navigation Structure
*   **Top Bar (Persistent):** Displays aggregate portfolio Net Asset Value (NAV), Daily PnL, global API connection status (Green/Red indicator), and the master "Kill All Routes" panic button (Admin only).
*   **Left Sidebar (Collapsible):** Dynamic routing based on RBAC. Contains primary view toggles: 
    *   `[Execution Terminal]`
    *   `[Portfolio & Risk]`
    *   `[Quant Analytics]`
    *   `[System Logs]` (Admin only).

### B. Core Module: The Execution Terminal
This is the primary screen for the `Trader` role. It must prevent cognitive overload while presenting all necessary data to approve a Phase 2 automated signal.
*   **Left Column (The Signal):** A clean panel displaying the raw JSON output from the Mathematical Engine translated into human-readable text. It explicitly highlights the Asset, Direction (Long/Short), Target $1R$ price, and the Expected Value $E(R)$.
*   **Center Column (The Chart):** A deeply integrated Lightweight Chart (TradingView). It plots the real-time Tick data overlaid with the *live* GARCH $\pm 2\sigma$ bands and OLS regression slope. This provides immediate visual proof of the mathematical anomaly.
*   **Right Column (The Action):** The Order Ticket. Pre-filled by the algorithm. The user sees the expected slippage, the required fractional Kelly size, and a highly prominent **[Authorize Execution]** button, alongside a **[Veto Signal]** button.

### C. Core Module: Portfolio & Risk Matrix
This is the primary screen for the `Admin` and `Analyst` roles.
*   **The Heatmap:** A visual matrix showing current exposure across all liquid assets. If the Copula model detects high tail-risk dependency between two active long positions, they flash orange/red to indicate clustered risk.
*   **Active Drawdown Gauge:** A dominant visual gauge tracking the current portfolio drawdown against the hard-coded VaR limit. As the portfolio approaches the system-wide kill switch threshold, the UI elements escalate from green to amber, to flashing red.

### D. UX Interaction Principles
*   **No Polling:** Users must never click a "Refresh" button. All prices, PnL metrics, and signal alerts must stream instantly via Server-Sent Events (SSE) or WebSockets.
*   **Confirmation Modals:** Any destructive action (e.g., manually liquidating a position or overriding the algo) requires a double-confirmation modal stating the explicit financial impact.

## 5. Documentation Maintenance
As the application scales and new modules (e.g., specific strategy pods, new data visualization screens) are added:
*   This document (`07_frontend_and_navigation.md`) must be routinely updated.
*   The mapping of Role $\rightarrow$ Allowed Routes must be meticulously tracked to ensure the dynamic error handling remains relevant.
*   All future frontend components must integrate with the central RBAC provider context.
