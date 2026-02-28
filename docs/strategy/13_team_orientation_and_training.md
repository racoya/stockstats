# Strategy 13: Technical Onboarding & Orientation Manual

## Welcome to STOCKSTATS
This document is mandatory reading for all engineers, quants, and operators joining the STOCKSTATS proprietary trading desk. 

**Our Objective:** We are not building a generic "crypto trading bot." We are building a mathematically rigorous, structurally defended Statistical Arbitrage and Volatility Engine. This document will bridge your existing software engineering skills with the specialized quantitative finance concepts ($E(R)>0$, Microstructure, Numba, Copulas) that power our architecture.

---

## Module 1: The Core Philosophy - Surviving the Microstructure

### 1.1 The Market is Hostile
If you build a simple script that says `IF Price > Moving Average THEN Buy`, you will lose all deployed capital within 72 hours. Why?
1.  **Adverse Selection:** The "Market" is actually composed of institutional High-Frequency Trading (HFT) algorithms operating in microseconds. If you send a "Market Order," they see it coming and instantly pull their liquidity, filling you at a terrible price (Slippage).
2.  **Trading Costs (Friction):** Every trade costs money. You pay exchange fees (Taker Fees) and you pay the Bid/Ask spread. 

### 1.2 The Minimum Viable Edge ($E(R) > 0$)
Every algorithm we write must mathematically prove it has a **Positive Expected Value**. This is the absolute, non-negotiable "Law of Gravity" in quantitative finance. If an algorithm cannot prove $E(R)>0$, it is gambling, not trading.
*   **The Baseline Math:** $E(R) = (Win Rate \times Average Win) - (Loss Rate \times Average Loss) - Friction$
*   Retail traders focus on *Win Rate*. Institutional quants focus on *Expectancy*. A 35% win rate strategy is wildly profitable if the average win is 4x the average loss.

### 1.3 Why Basic $E(R)$ Fails (And How We Fix It)
The formula above is a blunt instrument. It evaluates a strategy in a theoretical vacuum. Here is why amateur quant funds blow up using only that formula, and how STOCKSTATS is structurally designed to survive:

#### A. The Blind Spot of Variance (The "Smoothness" Problem)
*   **The Problem:** Strategy A makes $+0.2R$ on every trade. Strategy B makes $+10R$ once, and loses $-0.5R$ twenty times. Basic $E(R)$ says they are identical. In reality, Strategy B's variance will trigger a margin call before the big win ever happens.
*   **Our Solution (Model 05 - SQN):** We don't just calculate $E(R)$; we calculate the **System Quality Number (SQN)**, which penalizes "bumpy" equity curves by dividing the Expected Value by the Standard Deviation of the results. 

#### B. The Blind Spot of Averages (The Black Swan Problem)
*   **The Problem:** The formula relies on "Average Loss." Financial markets possess "Fat Tails." During a flash crash, stop-losses are skipped due to zero liquidity. Your "Average Loss" suddenly becomes a "Catastrophic Loss," instantly turning your $E(R)$ deeply negative.
*   **Our Solution (Models 06 & 12 - Copulas & VaR):** We assume the "Average Loss" lies to us. We use **Clayton Copulas** to mathematically model the probability of an extreme correlation crash (e.g., BTC and ETH both dropping 15% simultaneously) and override execution before the event hits.

#### C. The Blind Spot of Time (Capital Velocity)
*   **The Problem:** Strategy A has an $E(R)$ of $+1.0R$ per trade, but only trades once a month. Strategy B has an $E(R)$ of $+0.1R$ per trade, but trades 50 times a day. If you only look at the basic $E(R)$ *per trade*, Strategy A looks ten times better.
*   **Our Solution (Model 06 - Kelly Sizing):** We evaluate edges based on **Compound Annual Growth Rate (CAGR)**, not just per-trade $E(R)$. Strategy B is vastly superior because mathematically, turning capital over 50 times a day at $+0.1R$ compoundingly generates massive alpha over a month compared to a single $+1.0R$ event. We use the **Fractional Kelly Criterion** to mathematically size these high-velocity trades to maximize that compound growth without risking statistical ruin.


---

## Module 2: The Mathematical Models (The Brains)
You do not need a PhD in statistics to write the code, but you must understand *why* the code exists. We trade **Structural Inefficiencies**, not directional bets.

### 2.1 Volatility & GARCH (Model 01)
*   **The Concept:** Standard indicators like Bollinger Bands are fundamentally flawed because they assume market volatility is static. It is not. Volatility "clusters" (calm periods are followed by violent periods).
*   **Our Solution:** We use **GARCH(1,1)**. It analyzes the last 500 physical trades (ticks) and mathematically predicts what the volatility will be *in the next 5 minutes*. We only buy when the price physically breaks outside these dynamic, self-adjusting bands.

### 2.2 Statistical Arbitrage & Cointegration (Model 02)
*   **The Concept:** "Pairs Trading." Instead of guessing if Bitcoin (BTC) will go up or down, we look at the relationship between BTC and Ethereum (ETH). 
*   **The Math:** Historically, these two assets move together. If BTC suddenly shoots up but ETH stays flat, the "Spread" between them has widened. 
*   **Our Solution:** We calculate a **Z-Score** of that spread. If the Z-Score hits $+2.5$, we mathematically know the spread is broken. We Short BTC and Buy ETH simultaneously. We don't care if the whole market crashes; we only care that the *relationship* returns back to zero.

### 2.3 The Visual Flow of a Trade
```mermaid
graph TD
    classDef signal fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff;
    classDef risk fill:#ef4444,stroke:#fff,stroke-width:2px,color:#fff;
    classDef exec fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff;

    A("1. Ticks Arrive (BTC & ETH)"):::signal
    B("2. GARCH & Cointegration Math Run"):::signal
    C{"3. Is there an Edge? (E(R)>0)"}:::signal
    
    D{"4. Copula Risk Check\n(Is the portfolio safe?)"}:::risk
    E{"5. L2 Toxicity Check\n(Are HFTs spoofing?)"}:::risk
    
    F["6. VWAP Slicer Routes Micro-Orders"]:::exec

    A --> B --> C
    C -- Yes --> D
    C -- No --> A
    D -- Safe --> E
    D -- Risky --> A
    E -- Clean --> F
    E -- Toxic --> A
```

---

## Module 3: The Technology Stack (Why We Chose It)

To execute these math models, our code must be unbreakably fast and strictly decoupled.

### 3.1 Python + Numba (The Quant Engine)
*   **Why Python?** It has the best data science libraries (`numpy`, `statsmodels`, `xgboost`).
*   **The Problem:** Pure Python is too slow for processing 10,000 incoming trades per second.
*   **The Solution (Numba):** We use the `@njit` decorator on our heavy math loops. This literally compiles the Python code into C-level machine code just-in-time, making it 100x faster. 

### 3.2 The Dual Database Architecture (Crucial)
You will see two databases in our Docker stack. They never mix.
1.  **TimescaleDB (PostgreSQL):** The permanent SSD ledger. It stores billions of historical ticks. We use this strictly for **Backtesting** and training **Machine Learning** models. It is too slow for live trading.
2.  **Redis (The RAM Cache):** Sub-millisecond memory. When the Python engine needs to know the order book depth *right now* to execute a trade, it reads from Redis. Redis only remembers the last few minutes; TimescaleDB remembers everything forever.

### 3.3 The Next.js Operations Dashboard
We use TypeScript and React (Next.js) for the human command center. It visualizes the math (Grafana/Lightweight Charts) and allows human traders to manually authorize or veto executions during our Phase 1 rollout.

---

## Module 4: Execution & Risk Management (The Shields)

Making money is secondary. **Not losing capital to bugs or flash crashes is our primary directive.**

### 4.1 The VWAP Slicer (Model 04)
If the algorithm decides to buy $\$100,000$ of Ethereum, we **never** send a $\$100k$ market order. That would crush the exchange order book and we would lose $2\%$ immediately to slippage.
*   **Our Protocol:** The system slices the $\$100k$ block into twenty $\$5,000$ micro-orders over 5 minutes. This hides our structural footprint from predators.

### 4.2 The UUID State Machine (Model 13)
*   "Zombie Orders" destroy hedge funds. If we send an order, and my internet drops, did the order fill? Do we send it again?
*   **Our Protocol:** Every order is tagged with a cryptographic `clientOid` (UUID). The system operates a strict state machine (`PENDING` -> `FILLED`). If the API drops, our "Interrogator" loop aggressively pings the exchange using that exact UUID to find out exactly what happened before authorizing any new capital.

### 4.3 Value at Risk (VaR) Kill Switch (Model 12)
If a Black Swan event occurs (e.g., an unexpected global crisis), mathematical correlations go to $1.0$. Everything crashes together.
*   **Our Protocol:** The master VaR algorithm constantly calculates our total portfolio risk. If it detects a structural breach (drawdown $> 5\%$), it physically severs our API connections to the exchange, cancels all resting orders, and alerts the team via Slack.

---

## Conclusion & Next Steps
We are building a machine that expects the environment to be actively hostile. 
1.  **We clean the data (Hampel Filters):** We mathematically scrub out "rogue" exchange ticks caused by API errors so our models aren't triggered by fake data.
2.  **We prove the math (Cointegration):** We don't guess direction; we wait for the statistical spread between two highly correlated assets to break, knowing it is mathematically bound to revert.
3.  **We test the risk (Copulas):** Before executing that edge, we scan the entire portfolio for hidden correlation traps to avoid buying into a systemic "Black Swan" flash crash.
4.  **We hide the execution (VWAP Slicers):** When we deploy capital, we slice large orders into tiny micro-fractions to prevent predatory HFTs from seeing our size and stealing our alpha via slippage.

You are now conceptually calibrated to the STOCKSTATS architecture. Your immediate next step is to review `task.md` and the **Sprint 1 Implementation Plan**, where we begin physically scaffolding the TimescaleDB and Redis pipelines. 
