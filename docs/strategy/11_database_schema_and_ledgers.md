# Strategy 11: Quantitative Database Schemas & Immutable Ledgers

## 1. The Operational Objective
Before writing the first Python `asyncio` WebSocket loop for Phase 1, the underlying PostgreSQL / TimescaleDB data structures must be rigidly defined via Data Definition Language (DDL). 

A mathematical algorithm is only as robust as the data types underlying it. If cryptocurrency prices are saved as `FLOAT8` instead of `DECIMAL(24,8)`, the inherent floating-point arithmetic errors will compound across the Fractional Kelly position sizing matrices, eventually resulting in catastrophic precision failures at the exchange routing API.

This document serves as the mandatory SQL blueprint for the `backend/database/` environment initialization.

## 2. Core Architectural Philosophy
*   **Decoupled Instances:** The high-frequency `TimescaleDB` tick database MUST be physically decoupled from the Operations API (Node.js) `PostgreSQL` user management database to prevent ingestion latency spikes from freezing the Trading Desk UI.
*   **Strict Precision:** All cryptocurrency price and volume data must utilize fixed-point `DECIMAL(24,8)` to guarantee exact fractional persistence.
*   **The Idempotent Guarantee:** Every single order execution must enforce a `UNIQUE` index constraint on its proprietary `clientOid` UUID to mathematically eradicate the risk of API double-spending.

## 3. The `Ingestion Engine` Schema (TimescaleDB)
The high-frequency tick databases. This is where the massive volume of Level 1 trades is historically preserved for backtesting and real-time GARCH rolling windows.

### Table: `L1_tick_history`
This table is explicitly converted into a `TimescaleDB hypertable` partitioned heavily by the `timestamp` column. It stores the historically scrubbed data from the Numba Hampel Filter.

```sql
CREATE TABLE l1_tick_history (
    -- The composite primary key strategy for hypertable chunking
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL, -- e.g., 'BTC-USDT'
    exchange VARCHAR(30) NOT NULL, -- e.g., 'BINANCE'
    
    -- High precision storage. FLOAT8 is banned.
    price DECIMAL(24,8) NOT NULL,
    volume DECIMAL(24,8) NOT NULL,
    
    -- The execution side (Is this an active taker buying or selling?)
    -- Critical for VPIN and Phase 8 XGBoost Flow modeling
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    
    -- Raw exchange ID to prevent ingestion duplication on disconnects
    exchange_trade_id VARCHAR(100) NOT NULL, 

    PRIMARY KEY (time, symbol, exchange, exchange_trade_id)
);

-- Crucial: Convert the standard table into a TimescaleDB hypertable
-- It partitions the SSD data into 1-day chunks for extreme I/O velocity.
SELECT create_hypertable('l1_tick_history', 'time', chunk_time_interval => INTERVAL '1 day');
```

## 4. The `Operations API` Schema (PostgreSQL)
This structure governs the RBAC security, the Phase 1 Manual Logging, and the VaR circuit breaker configurations.

### Table: `rbac_users`
```sql
CREATE TABLE rbac_users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    -- Strict RBAC Enforcement
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'TRADER', 'ANALYST')),
    -- Security circuit breaker
    is_active BOOLEAN DEFAULT TRUE, 
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Table: `system_risk_parameters`
The global variables that strictly govern the Execution Engine logic (Strategy 05). The Python quantitative engine polls this table every 60 seconds to refresh its hard mathematical limits.

```sql
CREATE TABLE system_risk_parameters (
    parameter_id VARCHAR(50) PRIMARY KEY, -- e.g., 'MAX_PORTFOLIO_VAR'
    parameter_value DECIMAL(10,4) NOT NULL, -- e.g., 0.0500 (5%)
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- The admin who mathematically changed the system threshold
    updated_by UUID REFERENCES rbac_users(user_id) 
);
```

### Table: `immutable_execution_ledger` (The "Ground Truth")
The critical table serving as the origin logging for Phase 1 Manual Trading (Strategy 10) and the foundational training dataset for Phase 8 Machine Learning Models.

```sql
CREATE TABLE immutable_execution_ledger (
    -- Strategy 05 Reconciliation Requirement
    client_oid UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    
    -- When the human pushed the button, or the SOR fired
    execution_time TIMESTAMPTZ NOT NULL, 
    
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('LONG_ENTRY', 'LONG_EXIT', 'SHORT_ENTRY', 'SHORT_EXIT')),
    
    -- Expected vs Reality (For SQN Tracking)
    theoretical_price DECIMAL(24,8) NOT NULL,
    actual_fill_price DECIMAL(24,8) NOT NULL,
    fill_size DECIMAL(24,8) NOT NULL,
    
    -- 'MANUAL_PHASE_1' vs 'ALGO_COINTEGRATION'
    source_origin VARCHAR(50) NOT NULL, 
    -- If a human intervened or took the original trade
    author_user_id UUID REFERENCES rbac_users(user_id), 
    
    -- The Macro State when the transaction fired (Model 03)
    hmm_macro_regime_state INTEGER, 
    
    -- Order State Machine tracking
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'ACKNOWLEDGED', 'PARTIALLY_FILLED', 'FILLED', 'REJECTED'))
);

-- Crucial: This table is Immutable via PostgreSQL Triggers.
-- Once an execution order is written to this ledger, it CANNOT be updated or deleted by ANY User or API logic.
-- If an order fails, a NEW row is appended logging the failure. We must perfectly preserve the failure history for ML training.
```

## 5. Implementation Sequence for Phase 1
Before building the Python algorithms, we must perform the exact following structural initialization:
1.  Establish the `docker-compose.yml` to spin up the official TimescaleDB container image (not standard Postgres).
2.  Use a robust migration manager (e.g., `Alembic` for Python or `Prisma` for Node) to apply the aforementioned SQL structurally into the live volume.
3.  Ensure the Python application strictly casts all floating-point variables to Python `Decimal` classes *before* attempting `asyncpg` insertion.
