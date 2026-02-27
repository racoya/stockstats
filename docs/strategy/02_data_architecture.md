# Data Architecture: Infrastructure & Ingestion

## 1. Objective
To design a secure, fast, and highly reliable data ingestion and storage pipeline capable of processing real-time market ticks, historical depth, and alternative data sources to feed the Quantitative Logic Engine.

## 2. External Data Types & Market Sourcing

The system requires specific, institutional-grade external data inputs to calculate the GARCH, VWAP, and Mean Reversion formulas without latency lag. Retail-grade historical OHLCV candles are entirely insufficient for the core algorithms.

### A. Level 1 (L1) Top of Book (BBO)
*   **Requirement:** Continuous real-time WebSocket feeds of the Best Bid and Offer (BBO).
*   **Module Consumer:** The *Execution Routing Engine*.
*   **Purpose:** Required to calculate the real-time bid/ask spread (friction coefficient) on every tick before the logic engine authorizes a signal.

### B. Level 2 (L2) Order Book Depth
*   **Requirement:** Real-time and historical limits resting in the order book (Depth of Market - DOM), up to $X$ levels deep.
*   **Module Consumer:** The *Smart Order Router (SOR)* and *VWAP normalizer*.
*   **Purpose:** The SOR must process L2 depth dynamically to fraction block orders. If the engine needs to execute a $50k order, it must know exactly how much volume sits at the immediate bid/ask before crossing the spread to calculate expected slippage vs. the $1R$ risk limit.

### C. Tick-Level Aggregated Trades (Time and Sales)
*   **Requirement:** An append-only stream of every single executed trade (Price, Size, Timestamp, Taker Side).
*   **Module Consumer:** The *Mathematical Logic Engine*.
*   **Purpose:** 
    *   **GARCH Volatility:** The variance models ($\sigma$) require tick-level inputs to instantly detect market shocks ($\epsilon^2$) rather than waiting for a 1-minute candle to close.
    *   **VWAP Normalization:** The real-time VWAP equation ($P_{VWAP} = \frac{\sum P \cdot Q}{\sum Q}$) requires exact tick price ($P$) and tick volume ($Q$) matching against historical timestamps.

### D. Alternative Data Sourcing (Future Phase)
*   Infrastructure must be extensible to ingest non-price data (e.g., on-chain metrics, funding rates, options open interest) to feed secondary predictive models.

## 3. Storage Architecture (The Data Lake & Warehouse)
The system must support two entirely different read/write profiles: high-speed, append-only tick writing and complex, massive historical read queries for backtesting.

*   **Real-Time Cache (In-Memory):** Redis cluster. Used purely to hold the most recent *N* minutes of tick data to actively calculate real-time standard deviation ($\sigma$) bands and the slope ($m$) parameter instantly.
*   **Time-Series Database (The Core):** InfluxDB, TimescaleDB, or ClickHouse. Optimized specifically for time-stamped financial data. Stores minute-by-minute and tick-level history for fast retrieval by the backtesting engine.
*   **Relational Storage (Operations):** PostgreSQL securely hosts user data, trader execution logs, API keys (encrypted), and system auditable events.

## 4. Normalization and Pre-Processing
Data arriving from various sources (Crypto vs. Equities) will have different formats, timezones, and definitions of a "tick."
*   All incoming data must pass through a **Normalization Layer** that strips exchange-specific formatting and standardizes it into a unified internal schema (e.g., strictly UTC timestamps, standardized symbol mapping `BTC-USD` vs `BTC/USDT`).
*   **Data Quality Checks:** The ingestion engine must detect and handle missing data points, null values, or extreme API errors (e.g., a "flash crash" print that is an exchange glitch rather than a real trade).

## 5. Security and Access
*   Database access is strictly firewalled from the public internet.
*   The system uses an event-driven queue (e.g., Apache Kafka or RabbitMQ) to decouple the data ingestion from the Logic Engine, ensuring that a database hiccup does not crash the live trading process.
