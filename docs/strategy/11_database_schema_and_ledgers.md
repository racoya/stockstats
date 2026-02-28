# Strategy 11: Quantitative Database Architecture & Immutable Ledgers

## 1. The Operational Objective
Before writing the first Python `asyncio` WebSocket loop, the underlying PostgreSQL / TimescaleDB data structures must be rigidly defined via Data Definition Language (DDL). 

A mathematical algorithm is only as robust as the data types underlying it. If cryptocurrency prices are saved as `FLOAT8` instead of `DECIMAL(24,8)`, the inherent floating-point arithmetic errors will compound across the Fractional Kelly position sizing matrices, eventually resulting in catastrophic precision failures at the exchange routing API.

This document serves as the mandatory SQL blueprint, detailing the explicit table relationships, indexing rules, and hypertable partition strategies.

## 2. Entity-Relationship Diagram (ERD)
The database is strictly divided into two distinct domains: the high-velocity **TimescaleDB Tick Hub** (optimizing for massive `INSERT` volume) and the highly relational **PostgreSQL Operations Hub** (optimizing for RBAC and cryptographic auditing).

```mermaid
erDiagram
    %% The High-Velocity TimescaleDB Domain
    L1_TICK_HISTORY {
        timestamptz time PK "Hypertable Partition Key"
        varchar(20) symbol PK "e.g., BTC/USD"
        varchar(30) exchange PK
        varchar(100) exchange_trade_id PK
        decimal(24,8) price
        decimal(24,8) volume
        varchar(4) side "BUY or SELL"
        boolean is_scrubbed "Hampel Filter pass"
    }

    L2_ORDERBOOK_SNAPSHOT {
        timestamptz time PK "Hypertable Partition Key"
        varchar(20) symbol PK
        varchar(30) exchange PK
        jsonb bids "Top 50 levels via websocket"
        jsonb asks "Top 50 levels via websocket"
        decimal(10,4) obi_ratio "Pre-calculated Order Book Imbalance"
    }

    %% The Relational Operations Domain
    RBAC_USERS {
        uuid user_id PK
        varchar(255) email UK
        varchar(255) hashed_password
        varchar(20) role "ADMIN, TRADER, ANALYST"
        boolean is_active
    }

    SYSTEM_RISK_PARAMETERS {
        varchar(50) parameter_id PK "e.g., MAX_VAR"
        decimal(10,4) parameter_value
        timestamptz updated_at
        uuid updated_by FK "Points to RBAC_USERS"
    }

    IMMUTABLE_EXECUTION_LEDGER {
        uuid client_oid PK "Generated pre-execution"
        timestamptz execution_time
        varchar(20) symbol
        varchar(20) action "LONG_ENTRY, SHORT_EXIT etc"
        decimal(24,8) theoretical_price
        decimal(24,8) actual_fill_price
        decimal(24,8) fill_size
        varchar(50) source_origin "ALGO vs MANUAL"
        integer hmm_macro_regime_state
        varchar(20) status
        uuid author_user_id FK "Points to RBAC_USERS if manual"
    }
    
    SECURITY_AUDIT_LOG {
        uuid log_id PK
        timestamptz timestamp
        uuid user_id FK
        varchar(50) action_type "LOGIN, OVERRIDE, EXPORT"
        jsonb metadata "Contextual payload"
        inet ip_address
    }

    %% Defining the Relationships
    RBAC_USERS ||--o{ SYSTEM_RISK_PARAMETERS : "Admin Updates"
    RBAC_USERS ||--o{ IMMUTABLE_EXECUTION_LEDGER : "Trader Executes"
    RBAC_USERS ||--o{ SECURITY_AUDIT_LOG : "Generates Events"
    
    %% Note: The TimescaleDB tables run independently and don't physically join 
    %% with the Operations tables to prevent locking during high-frequency ingestion.
```

## 3. The `Tick Ingestion Engine` Schema (TimescaleDB)
This is the lifeblood of the quantitative engine. Standard PostgreSQL `B-Tree` indexes degrade exponentially when ingesting millions of rows per day. We explicitly utilize the `TimescaleDB` extension to structure these as **Hypertables**.

### A. The Level 1 Trade History (`l1_tick_history`)
*   **Purpose:** Stores every physical trade executed on the exchange (Tick data). Used for calculating historical VWAP profiles and real-time GARCH $\sigma$-bands.
*   **The Schema Engineering:**
    ```sql
    CREATE TABLE l1_tick_history (
        time TIMESTAMPTZ NOT NULL,
        symbol VARCHAR(20) NOT NULL, 
        exchange VARCHAR(30) NOT NULL, 
        price DECIMAL(24,8) NOT NULL,
        volume DECIMAL(24,8) NOT NULL,
        side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
        exchange_trade_id VARCHAR(100) NOT NULL, 
        is_scrubbed BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (time, symbol, exchange, exchange_trade_id)
    );

    -- 1. Create the Hypertable (Partitions physical disk space by day)
    SELECT create_hypertable('l1_tick_history', 'time', chunk_time_interval => INTERVAL '1 day');
    
    -- 2. Create a secondary index for fast querying by specific asset
    CREATE INDEX ix_symbol_time ON l1_tick_history (symbol, time DESC);
    ```
*   **The Relationship Logic:** The backend Python application polls this table via standard SQL (e.g., `SELECT * WHERE symbol = 'BTC' ORDER BY time DESC LIMIT 5000`) and passes the NumPy array into the math models. 

### B. The Level 2 Order Book Depth (`l2_snapshot`)
*   **Purpose:** Stores snapshots of the L2 resting liquidity. Crucial for the proprietary Order Book Imbalance (OBI) toxicity sensors (Model 15).
*   **Data Types:** Limit order depth is highly variable. We utilize PostgreSQL's binary `JSONB` format to efficiently store the bid/ask arrays without requiring 100 separate columns.
    ```sql
    CREATE TABLE l2_orderbook_snapshot (
        time TIMESTAMPTZ NOT NULL,
        symbol VARCHAR(20) NOT NULL,
        exchange VARCHAR(30) NOT NULL,
        bids JSONB NOT NULL,
        asks JSONB NOT NULL,
        obi_ratio DECIMAL(10,4), -- Pre-calculated by Python before insertion
        PRIMARY KEY (time, symbol, exchange)
    );
    SELECT create_hypertable('l2_orderbook_snapshot', 'time', chunk_time_interval => INTERVAL '1 day');
    -- Supports GIN indexing on the JSONB if we need to query specific price levels later
    ```

## 4. The Operations API Schema (PostgreSQL)
This domain controls the system's brain and tracks the humans. It is highly normalized (3NF) to ensure absolute data integrity.

### A. The RBAC Matrix (`rbac_users` & `system_risk_parameters`)
*   **Purpose:** To cryptographically enforce who can change the math parameters (Admins) versus who can solely deploy capital (Traders).
*   **The Relationship:** A `One-to-Many` relationship exists between `rbac_users` and `system_risk_parameters`. The database physically records *which* Admin ID altered the Master VaR limit.
    ```sql
    -- If Admin 'A' sets Max Leverage to 3x, the updated_by column permanently 
    -- links to Admin 'A's UUID.
    ALTER TABLE system_risk_parameters 
    ADD CONSTRAINT fk_admin_user 
    FOREIGN KEY (updated_by) REFERENCES rbac_users(user_id);
    ```

### B. The Immutable Execution Ledger (`immutable_execution_ledger`)
*   **Purpose:** The central nervous system for Phase 1 manual trading and the future training ground for Phase 8 Machine Learning (XGBoost).
*   **Data Integrity (The Golden Rule):** This table is structurally immutable. If a trade is executed, it is mathematically permanent. We enforce this via a database-level standard SQL Trigger.
    ```sql
    -- 1. The Trigger Function
    CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'CRITICAL: The Immutable Execution Ledger cannot be updated or deleted.';
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    -- 2. Applying the Trigger to block UPDATEs and DELETEs
    CREATE TRIGGER trg_immutable_ledger
    BEFORE UPDATE OR DELETE ON immutable_execution_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();
    ```
*   **SQN Tracking (Measuring Edge):** The columns `theoretical_price` and `actual_fill_price` are mandated. By querying the `DECIMAL` difference between these two columns across 1,000 trades, the backend instantly calculates the system's aggregate slippage degradation.

### C. The Authorization Ledger (`security_audit_log`)
*   **Purpose:** The system is managing proprietary capital. Complete operational transparency is required. This table acts as a Black Box flight recorder.
*   **Foreign Key Dependencies:** Every row ties back to an `rbac_users.user_id`. The Node.js Operations API middleware automatically appends to this table anytime an endpoint like `/api/admin/killswitch` is hit, storing the payload data perfectly in the `metadata` JSONB column.

## 5. Architectural Separation of Concerns
To guarantee maximum system throughput, the TimescaleDB hypertable arrays (`l1_tick_history`) are NEVER joined (`JOIN`) against the relational tracking tables (`rbac_users`). 

The Python Quantitative Logic Engine strictly connects to the `TimescaleDB` domain to run its fast NumPy mathematics, while the Node.js API Operations Server connects primarily to the Relational Domain to serve the React Dashboard. This architectural barrier prevents a massive frontend query by a Data Analyst from accidentally locking the tables the Execution Router needs to verify its active `clientOid`.
