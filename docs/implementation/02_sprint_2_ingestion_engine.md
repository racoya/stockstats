# Sprint 2 Implementation: The Ingestion Gateway

## The Objective
With the `TimescaleDB` and `Redis` databases live and isolated in Docker after Sprint 1, we must now build the software that pulls data into them from the exchanges.

The objective of Sprint 2 is to build the asynchronous Python Ingestion Engine. Its sole purpose is to connect to crypto exchanges (e.g., Binance, Kraken), listen to the live Level 1 Websocket trade streams, and inject those raw integers into our databases with absolute zero latency.

**Reference:** [Strategy 02 (Data Architecture)](../strategy/02_data_architecture.md)

---

## Step 1: The Asynchronous Architecture
We cannot use standard synchronous Python `requests` to pull 10,000 trades per second. We must build an `asyncio` Event Loop.

### 1.1 The CCXT Pro Websocket Router
We will utilize `ccxt.pro`, the asynchronous version of the CCXT library, to handle the heavy lifting of maintaining WebSocket connections.

*   **The 50-Asset Constraint:** We will define a static list of 50 assets (e.g., `BTC/USDT`, `ETH/USDT`, `SOL/USDT`).
*   **The Connection Matrix:** We will initialize a CCXT exchange instance and subscribe to the `watch_trades` stream for the 50 assets simultaneously.
*   **Error Handling:** The loop must cleanly handle `ConnectionClosedError` and `RateLimitExceeded` exceptions by implementing exponential backoff reconnection logic. *If the Websocket drops, the mathematical engine dies.*

## Step 2: The Dual-Injection Protocol
When a raw trade tick arrives via CCXT, it must be instantly routed to two different places simultaneously. 

### 2.1 The Permanent Archive (TimescaleDB)
Raw trades must be archived permanently for Phase 8 Machine Learning training.
*   **The Pipeline:** Use `asyncpg` within the Python Event Loop to fire asynchronous `INSERT` statements into TimescaleDB.
*   **The Table Schema:** 
    ```sql
    CREATE TABLE raw_trades (
        time        TIMESTAMPTZ NOT NULL,
        symbol      TEXT NOT NULL,
        price       DOUBLE PRECISION NOT NULL,
        volume      DOUBLE PRECISION NOT NULL,
        side        TEXT NOT NULL, -- 'buy' or 'sell'
        exchange    TEXT NOT NULL
    );
    SELECT create_hypertable('raw_trades', 'time');
    ```

### 2.2 The Volatile Cache (Redis Pub/Sub & ZSET)
The Quantitative Logic Engine (Sprint 4) cannot wait for TimescaleDB to write to SSD. It needs the data *now* to calculate the GARCH matrix.
*   **The Pipeline:** Use the `redis.asyncio` library to push the identical raw tick into Redis.
*   **The Structure:**
    *   **Pub/Sub:** Broadcast the tick on a channel (e.g., `trade:BTC-USD`). The Logic Engine will be "listening" to this channel to trigger recalculations.
    *   **Sorted Set (ZSET):** Store the tick in a Redis Sorted Set scored by its Unix Microsecond Timestamp. This allows us to instantly retrieve the "last 5 minutes of ticks" directly from RAM without touching Postgres.

## Step 3: Mitigation Protocol: The Microsecond Race Condition
During a flash crash, 10 trades can occur in the same microsecond on Binance. If we feed identical timestamps to our Pandas DataFrames in Sprint 4, the Matrix Inversion mathematics will throw a `Singular Matrix` (NaN) error and crash the bot.

*   **Implementation:** Before firing the `INSERT` into Postgres or Redis, we must run an aggregation function that checks for identical microsecond timestamps on the same asset.
*   **The Fix:** If it detects a collision, it coalesces the 10 trades into a single **Volume-Weighted Average Price (VWAP)** tick for that exact microsecond.
    *   *Volume:* Sum the volumes.
    *   *Price:* `(Price1*Vol1 + Price2*Vol2... ) / Total_Volume`

---
**Next Step:** Once the raw (but dirty) ticks are streaming perfectly into TimescaleDB and Redis, we move to **[Sprint 3: The Hampel Scrubber](03_sprint_3_hampel_filter.md)** to ensure exchange glitch data doesn't permanently mathematically poison the LEDGER.
