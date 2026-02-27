# STOCKSTATS

## Overview
The STOCKSTATS system is a proprietary, internally-developed algorithmic trading platform designed exclusively for our team. Its primary mandate is to execute quantitative trading strategies (focusing on mean reversion, intraday volatility profiling, and statistical arbitrage) across equities and cryptocurrency markets, ensuring a mathematically positive expectancy ($R > 0$).

Crucially, the system is designed as a **comprehensive operational platform**. It acts as the central hub for the internal trading desk, tracking individual trader performance, managing portfolio risk, and providing a unified dashboard for all trading operations, alongside automated signal generation.

## Documentation Navigation
The architecture and strategic goals of the project are documented in the `strategy/` directory:

1.  **[Project Vision & Scope](strategy/01_project_vision_and_scope.md)**: Executive summary and core mandates.
2.  **[Data Architecture](strategy/02_data_architecture.md)**: Infrastructure for data ingestion, storage, and caching (Cryptos, Equities).
3.  **[Mathematical Models](strategy/03_mathematical_models.md)**: The $R > 0$ logic engine, dynamic volatility (GARCH), regression models, and fractional Kelly sizing.
4.  **[Execution & Risk](strategy/04_execution_and_risk.md)**: Smart Order Routing (SOR), execution algorithms (TWAP/VWAP), and systemic kill switches.
5.  **[Internal Operations](strategy/05_internal_operations.md)**: Role-Based Access Control (RBAC), immutable audit ledgers, and live monitoring dashboards for the trading desk.
6.  **[Frontend & Navigation](strategy/06_frontend_and_navigation.md)**: Dynamic routing policies and contextual 404 error pages based on user security roles (Admin, Trader, Analyst).

## Tracking Progress
Project progress and upcoming tasks are tracked in the root [`task.md`](task.md) file.
