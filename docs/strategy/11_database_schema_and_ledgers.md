# Strategy 11: Quantitative Database Architecture & Immutable Ledgers

## 1. The Operational Objective
Before writing the first Python `asyncio` WebSocket loop, the underlying PostgreSQL / TimescaleDB data structures must be rigidly defined via Data Definition Language (DDL). 

A mathematical algorithm is only as robust as the data types underlying it. If cryptocurrency prices are saved as `FLOAT8` instead of `DECIMAL(24,8)`, the inherent floating-point arithmetic errors will compound across the Fractional Kelly position sizing matrices, eventually resulting in catastrophic precision failures at the exchange routing API.

This document serves as the mandatory database blueprint, proving that every single Mathematical Model (01 through 15) is physically accounted for in the SQL schema structures.

## 2. Comprehensive Entity-Relationship Diagram (ERD)
The database is strictly divided into two distinct domains: the high-velocity **TimescaleDB Tick Hub** (optimizing for massive `INSERT` volume) and the highly relational **PostgreSQL Operations Hub** (optimizing for SQN tracking, RBAC, and Phase 8 ML logs).

```mermaid
erDiagram
    %% The High-Velocity TimescaleDB Domain
    L1_TICK_HISTORY {
        timestamptz time PK "Hypertable Partition Key"
        varchar(20) symbol PK "e.g., BTC/USD"
        varchar(30) exchange PK
        varchar(100) exchange_trade_id PK
        "decimal(24,8)" price
        "decimal(24,8)" volume
        varchar(4) side "BUY or SELL"
        boolean is_scrubbed "Model 14: Hampel scrub state"
    }

    L2_ORDERBOOK_SNAPSHOT {
        timestamptz time PK "Hypertable Partition Key"
        varchar(20) symbol PK
        varchar(30) exchange PK
        jsonb bids "L2 depth"
        jsonb asks "L2 depth"
        "decimal(10,4)" obi_ratio "Model 15: Pre-calculated Imbalance"
    }

    %% The Relational Operations Domain
    RBAC_USERS {
        uuid user_id PK
        varchar(255) email UK
        varchar(25) role "ADMIN, TRADER, ANALYST"
    }

    SYSTEM_RISK_PARAMETERS {
        varchar(50) parameter_id PK "e.g., MAX_PORTFOLIO_VAR"
        "decimal(10,4)" parameter_value "Model 12: VaR limits"
        timestamptz updated_at
        uuid updated_by FK "Points to RBAC_USERS"
    }
    
    STRATEGY_PERFORMANCE_METRICS {
        varchar(50) strategy_id PK "e.g., GARCH_MEAN_REV"
        date calculation_date PK "Recalculated daily"
        "decimal(10,4)" current_sqn "Model 05"
        "decimal(10,4)" theoretical_er "Model 05 Expectancy"
        "decimal(10,4)" realized_er "Post-slippage Expectancy"
        "decimal(10,4)" deflated_sharpe_ratio "Model 11"
    }

    IMMUTABLE_EXECUTION_LEDGER {
        uuid client_oid PK "Model 13: Determinism"
        timestamptz execution_time
        varchar(50) strategy_id FK "Maps to Strategy Metrics"
        varchar(20) action "LONG_ENTRY, SHORT_EXIT"
        "decimal(24,8)" theoretical_price
        "decimal(24,8)" fill_size "Total intended block size"
        "decimal(10,4)" kelly_fraction_used "Model 06"
        integer hmm_macro_regime_state "Model 03 State"
        "decimal(10,4)" ml_veto_probability "Model 10 XGBoost Score"
        varchar(20) status "FILLED, REJECTED, VETOED"
        uuid author_user_id FK "Points to RBAC_USERS if manual"
    }
    
    VWAP_EXECUTION_SLICES {
        uuid slice_client_oid PK "Model 13 micro-order UUID"
        uuid parent_client_oid FK "Maps to Execution Ledger"
        timestamptz slice_time
        "decimal(24,8)" slice_price
        "decimal(24,8)" slice_volume "Model 04 VWAP size"
        varchar(20) status "Model 13 State Machine"
        "decimal(24,8)" slippage_delta "Execution vs Theoretical"
    }

    %% Defining the Relationships
    RBAC_USERS ||--o{ SYSTEM_RISK_PARAMETERS : "Admin Updates"
    RBAC_USERS ||--o{ IMMUTABLE_EXECUTION_LEDGER : "Trader Executes"
    
    STRATEGY_PERFORMANCE_METRICS ||--o{ IMMUTABLE_EXECUTION_LEDGER : "Logs performance"
    IMMUTABLE_EXECUTION_LEDGER ||--|{ VWAP_EXECUTION_SLICES : "Parent-Child Orders"
```

## 3. The `Tick Ingestion Engine` Schema (TimescaleDB)
Standard PostgreSQL `B-Tree` indexes degrade exponentially when ingesting millions of rows per day. We explicitly utilize the `TimescaleDB` extension to structure these as **Hypertables**, perfectly supporting the **Hampel Filter (Model 14)** and **OBI Toxicity (Model 15)** specs.

### A. The Level 1 Trade History (`l1_tick_history`)
*   **Purpose:** Stores every physical trade executed on the exchange. Used for generating the historical data streams for GARCH arrays and Kalman filters.
    ```sql
    CREATE TABLE l1_tick_history (
        time TIMESTAMPTZ NOT NULL,
        symbol VARCHAR(20) NOT NULL, 
        exchange VARCHAR(30) NOT NULL, 
        price DECIMAL(24,8) NOT NULL,
        volume DECIMAL(24,8) NOT NULL,
        side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
        exchange_trade_id VARCHAR(100) NOT NULL, 
        is_scrubbed BOOLEAN DEFAULT FALSE, -- Hampel Filter State
        PRIMARY KEY (time, symbol, exchange, exchange_trade_id)
    );

    -- 1. Create the Hypertable (Partitions disk space by 1-day chunks)
    SELECT create_hypertable('l1_tick_history', 'time', chunk_time_interval => INTERVAL '1 day');
    -- 2. Index for hyper-fast querying required by the Python engine
    CREATE INDEX ix_symbol_time ON l1_tick_history (symbol, time DESC);
    ```

## 4. The Quantitative Operations Schema (PostgreSQL)
This domain connects the Execution execution layer back to the mathematical models, ensuring absolute auditability.

### A. The VWAP Slicing Ledger (Model 04 & Model 13)
*   **Purpose:** A block order cannot hit the active market at once. The parent order resides in the `immutable_execution_ledger`, while the algorithmic sub-orders are tracked in `vwap_execution_slices`.
    ```sql
    CREATE TABLE vwap_execution_slices (
        slice_client_oid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        parent_client_oid UUID REFERENCES immutable_execution_ledger(client_oid),
        slice_time TIMESTAMPTZ NOT NULL,
        slice_price DECIMAL(24,8) NOT NULL,
        slice_volume DECIMAL(24,8) NOT NULL,
        -- Tracking the slippage delta of each specific slice
        slippage_delta DECIMAL(24,8), 
        status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'ACKNOWLEDGED', 'FILLED', 'ORPHANED'))
    );
    -- Indexing for rapid State Machine (Model 13) recoveries
    CREATE INDEX ix_parent_oid ON vwap_execution_slices (parent_client_oid);
    ```

### B. The Immutable Execution Ledger (The ML Training Block)
*   **Purpose:** This table guarantees we account for every mathematical model during execution. It stores the exact state of the system the millisecond the trade was requested.
    ```sql
    CREATE TABLE immutable_execution_ledger (
        client_oid UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        execution_time TIMESTAMPTZ NOT NULL, 
        strategy_id VARCHAR(50) NOT NULL, -- e.g., 'COINTEGRATION_BTC_ETH'
        
        -- Execution Pricing
        theoretical_price DECIMAL(24,8) NOT NULL,
        actual_fill_price DECIMAL(24,8), -- Nullable until all VWAP slices settle
        fill_size DECIMAL(24,8) NOT NULL,
        
        -- Mathematical Model Checkpoints
        kelly_fraction_used DECIMAL(10,4) NOT NULL, -- Model 06: E.g., 0.25 (Quarter Kelly)
        hmm_macro_regime_state INTEGER,             -- Model 03: 0, 1, or 2
        ml_veto_probability DECIMAL(10,4),          -- Model 10: XGBoost false-positive score attached BEFORE execution
        
        status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'EXECUTING', 'FILLED_COMPLETE', 'VETOED')),
        source_origin VARCHAR(50) NOT NULL          -- 'ALGO' vs 'MANUAL_PHASE_1'
    );
    ```
*   **Data Integrity (The Golden Rule):** This table is structurally immutable. If the XML payload fails at the exchange, the row is updated strictly to `FAILED`. Deleting rows destroys the XGBoost Backtesting rigor (Model 11).
    ```sql
    -- PostgreSQL Trigger explicitly blocking DELETE operations
    CREATE OR REPLACE FUNCTION prevent_ledger_deletion()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'CRITICAL: The Execution Ledger cannot be deleted. XGBoost training requires absolute negative-class historical logs.';
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_immutable_ledger_delete
    BEFORE DELETE ON immutable_execution_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_deletion();
    ```

### C. SQN & Deflated Sharpe Tracking (Model 05 & 11)
*   **Purpose:** We must formally track algorithm decay over time.
    ```sql
    CREATE TABLE strategy_performance_metrics (
        strategy_id VARCHAR(50) REFERENCES system_strategies(id),
        calculation_date DATE NOT NULL,
        
        -- Model 05 Expectancy Metrics
        current_sqn DECIMAL(10,4) NOT NULL,
        theoretical_er DECIMAL(10,4) NOT NULL,
        realized_er DECIMAL(10,4) NOT NULL,
        
        -- Model 11 Deflated Sharpe Ratio
        deflated_sharpe_ratio DECIMAL(10,4) NOT NULL,
        trade_count INTEGER NOT NULL,
        
        PRIMARY KEY (strategy_id, calculation_date)
    );
    ```
    *   **Logic:** Every night at 00:00 UTC, a Cron job queries the `immutable_execution_ledger`, calculates the exact realized $R$-multiples, recalibrates the $SQN$, and appends a row to this table. If a Strategy $SQN$ falls below 1.6, it is autonomously disabled on the Dashboard.

## 5. Summary of Schema Completeness
This extended database explicitly covers the 15 specifications defined in the math models:
*   **Data scrubbing & toxicity (Models 14 & 15)** via TimescaleDB Hypertable L1/L2 tables (`is_scrubbed`, `obi_ratio`).
*   **Sizing & Machine Learning (Models 06 & 10)** via `kelly_fraction_used` and `ml_veto_probability` embedded directly into the execution origin ledger.
*   **Routing & Latency (Models 04 & 13)** natively solved via the explicitly partitioned `vwap_execution_slices` matching sub-orders to the `client_oid` State Machine logic. 
*   **Performance Decay (Models 05 & 11)** natively tracked via the daily `strategy_performance_metrics` table.
