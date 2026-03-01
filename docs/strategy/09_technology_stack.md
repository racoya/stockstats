# Strategy 09: The Quantitative Technology Stack

## 1. The Operational Objective
To explicitly define the programming languages, LLVM compilers, frameworks, and infrastructure tooling utilized to build the STOCKSTATS quantitative engine. 

The stack fundamentally prioritizes matrix execution speed, mathematical precision, and scalable CI/CD development over standard web-app paradigms.

## 2. The Core Language Paradigms

### A. Python (The Quantitative Core)
Python is the undisputed institutional standard for mathematical modeling and continuous data science.
*   **Usage:** The Data Ingestion Gateway (Service 1), Quantitative Logic Engine (Service 2), and Execution Router (Service 3).
*   **The Matrix Acceleration (Numba JIT):** Pure Python is mathematically too slow for high-frequency tick scrubbing or real-time OBI volume profiling. We strictly utilize **Numba**, a Just-In-Time (JIT) compiler that translates Python functions directly into optimized machine code using the LLVM compiler library, achieving C-level iteration speeds.
*   **Key Dependencies:**
    *   `numpy` & `scipy`: High-performance vector operations and linear algebra manipulation for continuous time-series arrays.
    *   `statsmodels`: For OLS regression, Cointegration Eigenvalues (ADF tests), and Kalman Filter structural matrix updates.
    *   `arch`: For estimating GARCH(1,1) volatility models.
    *   `xgboost`: For the non-linear Machine Learning Meta-Labeling overlays.
    *   `ccxt` (Async): The unified crypto exchange REST/WebSocket library (handles cryptographic ECDSA signature signing for 100+ exchanges).

### B. TypeScript / Node.js (The Operations Layer)
TypeScript provides the strict architectural type safety required for operational UIs while maintaining the massive asynchronous ecosystem of the modern web.
*   **Usage:** The Operations REST API (Service 4) and the Frontend Command Center.
*   **Why TS over Python for Web:** Node.js/TypeScript handles asynchronous I/O (like pushing thousands of simultaneous WebSocket `ACKNOWLEDGED` updates to the frontend dashboard) structurally more efficiently than standard Python WSGI frameworks.

### C. The Mathematical Mandate: Why Python over Java / C++
It is a common reflexive impulse for enterprise software engineers to demand JVM-tuned Java or C++ for trading systems, citing execution speed. We have aggressively excluded Java and C++ from the STOCKSTATS architecture for three mathematically undeniable reasons:

1.  **The Sub-Millisecond Delusion:** STOCKSTATS is fundamentally a *Statistical Arbitrage* and *Mean Reversion* engine, not a pure High-Frequency Trading (HFT) nanosecond market-making engine. We generate edges measured in seconds/minutes, not microseconds. The $\approx 100$ microsecond execution advantage of a monolithic Java/C++ engine is mathematically neutralized the moment our payload hits the public internet and encounters the standard $20+$ millisecond API latency of global exchanges like Binance. We do not need nanosecond internal execution; we need millisecond execution, which Python easily achieves.
2.  **The LLVM Equalizer (`numba`):** The primary argument against Python is that the Global Interpreter Lock (GIL) and dynamic typing make array iteration unacceptably slow. We solve this not by changing languages, but by utilizing **Numba**. By wrapping our intensive mathematical functions (e.g., Hampel Filters, GARCH matrices) in `@njit`, we bypass the Python interpreter entirely. Numba uses the LLVM compiler library to translate our Python directly into optimized, C-level machine code just-in-time. We achieve Java speeds without writing Java boilerplate.
3.  **The R&D Friction (The Death of Java in Quant):** If a PhD quantitative researcher designs a new Copula dependency matrix, it can be tested in `pandas` and deployed to production in Python within 48 hours. Translating that same multidimensional matrix into Java requires massive boilerplate code, fractured library support, and mechanical engineering overhead that fundamentally destroys the strategy iteration cycle. Furthermore, **Phase 8 (ML Meta-Labeling)** mandates the use of `xgboost` gradient boosted trees. Python is the undisputed native language of global Machine Learning. Forcing an ML-driven quant desk into Java is architectural sabotage. We optimize for Time-to-Market and R&D velocity.

## 3. The Tech Stack Breakdown (Definitive Selections)

We have permanently eliminated ambiguity from the architectural blueprint. The following technologies are the final, non-negotiable selections for the STOCKSTATS engine.

### I. Frontend (The Command Center)
*   **Framework Selection: Next.js (React)** 
    *   *Why not Vue, Angular, or Vite?* Next.js provides unmatched Server-Side Rendering (SSR) capabilities which perfectly compliment the heavy initial JSON payloads required for initializing 500-period charting matrices. It also natively supports API routes, allowing us to build secure, server-side mid-tier proxies without spinning up a separate Node server.
*   **State Management: Zustand & React Query**
    *   *Why not Redux?* Redux requires massive boilerplate for a UI that fundamentally just acts as a passive surveillance radar. Zustand provides ultra-lightweight global state (JWT Roles), while React Query natively handles the aggressive polling and caching of the JSON feeds.
*   **Design Typography:** Tailwind CSS + shadcn/ui. (Strict dark-mode protocol to reduce optical fatigue during continuous monitoring).
*   **Charting Engine:** TradingView Lightweight Charts natively integrated via WebGL to prevent DOM locking when rendering 10,000+ localized GARCH ticks.

### II. Backend (The Microservices)
*   **The Math/Execution Node Selection: Python + FastAPI**
    *   *Why not Django or Flask?* Django is a heavy, synchronous monolith violently incompatible with High-Frequency WebSocket ingestion. Flask's async support is bolted-on. FastAPI was built from the ground up on `Starlette` and `uvicorn`, offering native asynchronous I/O and Pydantic data validation, which physically guarantees our JSON payloads have not drifted before hitting the Execution Router.
*   **The Operations Web-Tier: Next.js API Routes (TypeScript)**
    *   *Why not a separate Express server?* Consolidating the Role-Based JWT middleware and frontend routes into the singular Next.js monolith drastically reduces Docker overhead on the Basement Server while maintaining strict TypeScript interface parity between the frontend graphs and backend SQL queries.

### III. Data Storage & System Caching
*   **The Quantitative Ledger: TimescaleDB**
    *   *Why not MongoDB or AWS Timestream?* MongoDB is a NoSQL document store; statistical mathematics (like rolling variances and Cointegration) fundamentally demand relational, columnar arrays, which NoSQL mangles. TimescaleDB is a native PostgreSQL extension. It gives us the aggressive, high-velocity `INSERT` speeds required for tick data (via partitioning/hypertables) while preserving 100% standard SQL logic for the complex relational `immutable_execution_ledger`.
*   **The High-Frequency Cache: Redis**
    *   *Why not Memcached?* Memcached is fundamentally ephemeral. Redis offers persistence-to-disk capabilities, advanced data structures (like Sorted Sets for maintaining the exact top 100 L2 Order Book Imbalances), and native Pub/Sub.
*   **The Event Bus Selection: Redis Pub/Sub**
    *   *Why not Apache Kafka?* Kafka is an institutional titan, but deploying an internal ZooKeeper/Kafka cluster on our singular Basement Server requires $>8GB$ of dedicated RAM, creating an unacceptable localized hardware bottleneck. Redis Pub/Sub is incredibly lightweight, perfectly fulfilling the event-driven requirements of Phases 1-8. We will re-evaluate Kafka strictly during the Phase 9 AWS Migration.

## 4. DevOps & Production Architecture
*   **Containerization:** Docker. Every isolated microservice must have its own strict `Dockerfile` to guarantee perfect mathematically parity between the Quant's local laptop, the Basement Server, and the future AWS production cluster.
*   **Orchestration (Phases 1-8):** Docker Compose. All Production trading occurs physically on the local Basement Server to minimize costs and maximize iteration speed during early autonomy.
*   **Orchestration (Phase 9 Future):** AWS Elastic Container Service (ECS). Once the autonomous Basement Server proves profitable over several months, the Docker networks are migrated to a dedicated Tokyo VPC for sub-millisecond latency arbitrage.
*   **CI/CD Isolation:** GitHub Actions. Every Git push to the `main` branch must physically trigger automated Python unit tests evaluating the mathematical models against static $2021$ mock data before a Docker deploy is structurally permitted.
