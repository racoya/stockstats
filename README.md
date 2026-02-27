# STOCKSTATS

## Overview
The STOCKSTATS system is a proprietary, internally-developed algorithmic trading platform designed exclusively for our team. Its primary mandate is to execute quantitative trading strategies (focusing on mean reversion, intraday volatility profiling, and statistical arbitrage) across equities and cryptocurrency markets, ensuring a mathematically positive expectancy ($R > 0$).

Crucially, the system is designed as a **comprehensive operational platform**. It acts as the central hub for the internal trading desk. While the ultimate goal is fully autonomous execution, the system is being built in phases: starting as a sophisticated manual desk tracking individual trader performance and portfolio risk, and eventually maturing into an automated signal generation and execution engine.

## Documentation Navigation
The architecture and strategic goals of the project are documented in the `strategy/` directory:

0.  **[Strategic Roadmap](strategy/00_roadmap.md)**: The phased evolution from manual execution to full automation.
1.  **[Project Vision & Scope](strategy/01_project_vision_and_scope.md)**: Executive summary and core mandates.
2.  **[Data Architecture](strategy/02_data_architecture.md)**: Infrastructure for data ingestion, storage, and caching (Cryptos, Equities).
3.  **[Mathematical Models](strategy/03_mathematical_models.md)**: The $R > 0$ logic engine, dynamic volatility (GARCH), regression models, and fractional Kelly sizing.
    *   *See the **[Mathematical Models Index](models/00_model_index.md)** for the 12 deep-dive algorithmic whitepapers (Kalman Filters, OU Half-Life, Copulas, etc).*
4.  **[Notification Engine](strategy/04_notification_engine.md)**: Real-time alerts, Slack/SMS integration, and signal formatting.
5.  **[Execution & Risk](strategy/05_execution_and_risk.md)**: Smart Order Routing (SOR), execution algorithms (TWAP/VWAP), and systemic kill switches.
6.  **[Internal Operations](strategy/06_internal_operations.md)**: Role-Based Access Control (RBAC), immutable audit ledgers, and live monitoring dashboards for the trading desk.
7.  **[Frontend & Navigation](strategy/07_frontend_and_navigation.md)**: Dynamic routing policies and contextual 404 error pages based on user security roles (Admin, Trader, Analyst).
8.  **[Backend Architecture](strategy/08_backend_architecture.md)**: Microservices design, internal APIs, message brokers (Kafka/RabbitMQ), and database ledger schemas.
9.  **[Technology Stack](strategy/09_technology_stack.md)**: Python quantitative core, TypeScript operations layer, infrastructure, and deployment CI/CD.

## Tracking Progress
Project progress and upcoming tasks are tracked in the root [`task.md`](task.md) file.
