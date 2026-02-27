-- STOCKSTATS Immutable Ledger Schema
-- Database: PostgreSQL (with TimescaleDB extension intended for future tick-data)

-- 1. Enum Types for Strict State Enforcement
CREATE TYPE order_status AS ENUM (
    'PENDING_SUBMIT',
    'ACKNOWLEDGED',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'UNKNOWN',
    'FAILED_TO_SUBMIT'
);

CREATE TYPE order_side AS ENUM ('BUY', 'SELL');
CREATE TYPE order_type AS ENUM ('MARKET', 'LIMIT', 'VP', 'TWAP');
CREATE TYPE user_role AS ENUM ('ADMIN', 'TRADER', 'RISK_MANAGER', 'VIEWER');

-- 2. Internal Operations & RBAC
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'VIEWER',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action_type VARCHAR(100) NOT NULL, -- e.g., 'MANUAL_OVERRIDE_KILL_SWITCH'
    target_resource VARCHAR(255),
    old_value JSONB,
    new_value JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);

-- 3. The Logic Engine Outputs (Signals)
CREATE TABLE mathematical_signals (
    signal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL, -- e.g., 'COINTEGRATION_STATARB_BTC_ETH'
    target_asset VARCHAR(50) NOT NULL,
    direction order_side NOT NULL,
    z_score NUMERIC(10, 4),
    half_life_minutes NUMERIC(10, 2),
    ml_win_probability NUMERIC(5, 4), -- Output from Meta-Labeling
    suggested_size_usd NUMERIC(15, 2),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_executed BOOLEAN DEFAULT FALSE
);

-- 4. The Execution State Machine (The Reconciliation Ledger)
CREATE TABLE execution_orders (
    client_oid UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- The Deterministic ID sent to Exchange
    signal_id UUID REFERENCES mathematical_signals(signal_id), -- Can be NULL for manual desk trades
    user_id UUID REFERENCES users(user_id), -- The Trader who authorized it (if manual)
    exchange VARCHAR(50) NOT NULL, -- e.g., 'BINANCE', 'IBKR'
    symbol VARCHAR(50) NOT NULL,
    side order_side NOT NULL,
    type order_type NOT NULL,
    quantity_requested NUMERIC(20, 8) NOT NULL,
    price_limit NUMERIC(20, 8),
    
    -- State Machine Tracking
    status order_status NOT NULL DEFAULT 'PENDING_SUBMIT',
    exchange_order_id VARCHAR(255), -- The ID returned by the exchange *after* submission
    quantity_filled NUMERIC(20, 8) DEFAULT 0,
    average_fill_price NUMERIC(20, 8),
    fee_incurred NUMERIC(20, 8),
    fee_asset VARCHAR(10),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Indexes for fast quantitative lookup
CREATE INDEX idx_execution_orders_status ON execution_orders(status);
CREATE INDEX idx_signals_model_name ON mathematical_signals(model_name, generated_at);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Function to perfectly auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_execution_orders_updated_at
BEFORE UPDATE ON execution_orders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
