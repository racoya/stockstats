# Data Architecture: Infrastructure & Ingestion

## 1. Objective
To design a secure, fast, and highly reliable data ingestion and storage pipeline capable of processing real-time market ticks, historical depth, and alternative data sources to feed the Quantitative Logic Engine.

## 2. Market Data Sourcing
The system requires institutional-grade data to calculate precise Mean Reversion and Volatility metrics without latency lag.

*   **Cryptocurrency:** WebSockets for real-time bid/ask and tick data (e.g., Binance, Coinbase Pro APIs, or aggregators like Kaiko/Tardis for historical).
*   **Traditional Equities:** Direct API feeds (e.g., Polygon.io, Alpaca, or Interactive Brokers API) for SIP consolidated real-time tape and historical OHLCV data.
*   **Alternative Data (Future Phase):** Infrastructure must be extensible to ingest non-price data (e.g., on-chain metrics, funding rates, options open interest).

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
