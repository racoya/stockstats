# Technology Stack: Languages, Frameworks, & Tooling

## 1. Objective
To explicitly define the programming languages, frameworks, and infrastructure tooling that will be utilized to build the STOCKSTATS system, prioritizing execution speed, mathematical precision, and scalable development.

## 2. The Core Language Paradigms

### A. Python (The Quantitative Core)
Python is the undisputed industry standard for financial modeling and data science.
*   **Usage:** The Data Ingestion Engine, Quantitative Logic Engine, and Execution Routing Engine.
*   **Key Libraries:**
    *   `pandas` & `numpy`: High-performance vector operations and DataFrame manipulation for time-series data.
    *   `statsmodels` & `scipy`: For OLS regression, Cointegration (ADF), and advanced statistical tests.
    *   `arch`: For estimating GARCH volatility models.
    *   `hmmlearn`: For Gaussian Hidden Markov Models (Regime Detection).
    *   `ccxt`: The unified crypto exchange trading library (handles signature signing and unified API endpoints for 100+ exchanges).

### B. TypeScript (The Operations Layer)
TypeScript provides the strict type safety required for operational UIs while maintaining the massive ecosystem of the modern web.
*   **Usage:** The Operations API (Backend) and the Trading Desk Dashboard (Frontend).
*   **Why TS over Python for Web:** Node.js/TypeScript handles asynchronous I/O (like pushing thousands of WebSocket updates to the frontend dashboard) highly efficiently.

### C. The Conscious Exclusion of Java / C++
While Java and C++ are the dominant languages in traditional High-Frequency Trading (HFT) firms, they have been intentionally excluded from the initial STOCKSTATS architecture for several strategic reasons:
*   **Latency vs. Strategy:** STOCKSTATS is a *Statistical Arbitrage* and *Mean Reversion* engine, not a pure HFT market-making engine. We are trading on statistical edges measured in seconds/minutes, not nanosecond front-running. The sub-millisecond execution advantage of Java/JVM tuning is negated by the standard API latency of cryptocurrency exchanges.
*   **Quantitative Friction:** The Python ecosystem (`pandas`, `numpy`, `scipy`) allows quantitative researchers to conceptualize, backtest, and deploy a complex math model (like GARCH) in days. Translating that same model into Java requires significantly more boilerplate code and engineering overhead, slowing down the strategy iteration cycle.
*   **Talent & Ecosystem:** The modern web development ecosystem and open-source crypto libraries (like `ccxt`) are built almost entirely around Node.js (TypeScript) and Python. Forcing a Java architecture would require building many custom library wrappers from scratch.

## 3. The Tech Stack Breakdown

### Frontend (Trading Desk Dashboard)
*   **Framework:** Next.js (React) or Vite + React. Selected for component modularity and deep ecosystem support for complex financial charting.
*   **State & Data Fetching:** React Query (for caching API responses) and contextual Zustand (for lightweight global state, e.g., the active user's RBAC role).
*   **Styling:** Tailwind CSS (for rapid prototyping of complex data tables and dashboards) combined with customized, premium component libraries (e.g., shadcn/ui or Radix).
*   **Charting:** Lightweight Charts (TradingView) or Recharts for rendering the real-time $\sigma$-bands alongside actual execution points.

### Backend (The Microservices)
*   **The Math/Execution Services:** Python 3.11+ running asynchronous architecture (`asyncio`, `aiohttp`, or `FastAPI` for internal endpoints).
*   **The Operations API:** Node.js with Express or NestJS (TypeScript), highly optimized for managing JWT authentication, GraphQL/REST endpoints for the frontend, and SSE logic.

### Data Storage & Caching
*   **Relational DB (Users, Logs, Audits):** PostgreSQL. Unmatched reliability and robust JSONB support.
*   **Time-Series DB (Market Data):** TimescaleDB (which is a PostgreSQL extension, keeping the stack unified) or InfluxDB.
*   **In-Memory Cache:** Redis. Essential for maintaining the real-time Order Book depth and the rolling $N$-minute tick array for instant GARCH updates.
*   **Message Broker:** Redis Pub/Sub (for lighter loads) migrating to RabbitMQ or Apache Kafka (for guaranteed event delivery) as the system scales to full autonomy.

## 4. Infrastructure & DevOps
*   **Containerization:** Docker. Every isolated microservice must have its own `Dockerfile` to guarantee perfect parity between the developer's laptop and the live production server.
*   **Orchestration:** Docker Compose (Phase 1 local deployment) migrating to Kubernetes (K8s) or AWS ECS for live production.
*   **CI/CD:** GitHub Actions. Every push to the `main` branch must trigger automated unit tests evaluating the mathematical models against static mock data before a deploy is permitted.
