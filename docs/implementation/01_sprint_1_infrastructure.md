# Sprint 1 Implementation: Core Infrastructure

## The Objective
To physically construct the Phase 1 Foundation of the STOCKSTATS architecture on the local machine. We must scaffold the isolated dual-database environment (TimescaleDB for permanent SSD storage, Redis for sub-millisecond RAM caching) and establish the highly-controlled Python environment.

**Reference:** [Strategy 02 (Data Architecture)](../strategy/02_data_architecture.md), [Strategy 09 (Tech Stack)](../strategy/09_technology_stack.md)

---

## Step 1: The Dockerized Storage Layer

The bedrock of a quantitative system is immutable, sterilized data. We do not install databases natively on the macOS host; we isolate them in Docker to guarantee 1:1 parity with the future AWS production cluster.

### 1.1 The `docker-compose.yml` File
We will create a `docker-compose.yml` file at the root of the project to orchestrate the internal network.

**Specifications:**
*   **TimescaleDB:** We will pull the official `timescale/timescaledb-ha:pg15` image. 
    *   *Why HA?* The High Availability image includes the tools required for our future Step 3.B "Off-Site S3 WAL Archiving" mandate (Strategy 11).
    *   *Volume:* We must map a local physical directory (e.g., `./docker-volumes/timescaledb/`) to `/home/postgres/pgdata/data` to ensure our mathematical data survives container restarts.
    *   *Port:* `5432:5432`
*   **Redis:** We will pull the official `redis:7-alpine` image to maintain a tiny infrastructural footprint.
    *   *Volume:* Map `./docker-volumes/redis/` to `/data`.
    *   *Port:* `6379:6379`
    *   *Persistence:* We will configure Redis to save to disk occasionally (`--save 60 1`), but its primary role is volatile L2 OBI array caching.

### 1.2 Validation Check
*   Run `docker-compose up -d`.
*   Use a tool like TablePlus or DBeaver to successfully connect to `localhost:5432` with the defined credentials.
*   Run `SELECT default_version, installed_version FROM pg_available_extensions WHERE name = 'timescaledb';` to mathematically verify the time-series extension is active.

---

## Step 2: The Python Quantitative Core

The `backend/` directory houses the statistical brains of the operation. We must isolate its dependencies flawlessly.

### 2.1 Virtual Environment
We will create a strict `venv` to prevent global macOS package collisions.
*   `python3.11 -m venv venv`
*   `source venv/bin/activate`

### 2.2 The `requirements.txt` Freeze
We will define the exact libraries required for the Ingestion and Logic engines. Version locking is critical to prevent a future update from breaking the Numba LLVM compiler.

**Core Packages:**
*   `ccxt[async]` (For exchange routing)
*   `asyncio`, `aiohttp` (For the Websocket ingestion loops)
*   `numpy==1.26.4`, `pandas==2.2.1` (For array manipulation)
*   `numba==0.59.1` (For JIT-compiling the Hampel Filter and Cointegration math)
*   `asyncpg` (For high-velocity Inserts into TimescaleDB without blocking the Python event loop)
*   `redis.asyncio` (For sub-millisecond Pub/Sub and caching)

### 2.3 Directory Scaffolding
We will build the physical folder structure required for the microservice:
```plaintext
STOCKSTATS/
├── backend/
│   ├── main.py                # The entrypoint for the Docker service
│   ├── core/                  # The Math (Hampel, GARCH, Cointegration)
│   ├── ingestion/             # The WebSocket Listeners (Binance, Kraken)
│   ├── execution/             # (Phase 3) The Manual Kelly Sizing formatter
│   └── database/              # The asyncpg connection pools and Redis wrappers
```

## Step 3: Git & Environment Security

*   Create `.gitignore` to explicitly ban `venv/`, `docker-volumes/`, `__pycache__/`, and `.env` from ever touching the repository.
*   Create an `.env.example` template detailing the PostgreSQL connection strings and the (blank) Binance `API_KEY` and `API_SECRET`.

---
**Next Step:** Once Sprint 1 is executed and the baseline databases are running efficiently on `localhost`, we immediately pivot to **[Sprint 2: The Ingestion Engine](02_sprint_2_ingestion_engine.md)** to begin physically pulling L1 ticks.
