# Mathematical Models: The Logic Engine Core

## 1. Objective
To formalize the mathematical principles, statistical boundaries, and execution logic that govern the $R > 0$ intelligence mandate. The system uses strict formulas, not discretionary feelings.

## 2. Dynamic Volatility & Mean Reversion
The core engine identifies statistical anomalies (deviation from the mean), but must dynamically adjust to changing market environments to prevent entering trades against structural macro shifts.

*   **The Baseline:** Calculating linear regression lines ($m$, $n$) over defined $X$-period rolling windows.
*   **Dynamic Sigma ($\sigma$) Bands:** Instead of a static standard deviation algorithm, we will implement conditional variance models (e.g., **GARCH - Generalized Autoregressive Conditional Heteroskedasticity**). 
    *   *Logic:* If the market suddenly becomes highly volatile (e.g., news event), the GARCH model will instantly expand the $+/- 3\sigma$ bands, preventing premature entry signals that a static model would trigger.
*   **Momentum Context:** Mean reversion signals ($\pm 3X / 4X$ hits) are only valid if they align with (or signal the exhaustion of) the underlying regression slope ($m$).

## 3. Intraday Liquidity Mapping
Time-of-day normalization is used as an execution filter.

*   **Volume-Weighted Average Price (VWAP) Normalization:** We map historical 20-minute interval liquidity profiles.
    *   *Logic:* If the system signals a "buy" at 03:00 AM, but historical normalization shows this interval accounts for less than 1% of daily volume, the system flags a "Low Liquidity Environment" warning and either vetoes the trade or automatically fractions the order size to prevent slippage.

## 4. The R > 0 Expectancy Function
The guiding principle of every trade constraint.

*   **The Formula:** `R = [Win_Rate * Average_Win] - [(1 - Win_Rate) * Average_Loss]`
*   **Real-World Friction:** The Logic Engine must actively deduct estimated slippage, exchange fees, and bid/ask spread costs from the theoretical $R$ before approving any algorithm. If $R_{friction} < 0$, the strategy is suspended.

## 5. Multi-Asset Correlation & Portfolio Sizing
To survive drawdowns, we mathematically distribute risk.

*   **Copula Correlation Modeling:** Standard correlation (Pearson) fails during market crashes because all risk assets correlate to 1.0. We use Copulas to mathematically model *joint tail dependency* (the likelihood that Asset A and Asset B both crash $\ge 3\sigma$ simultaneously).
*   **Fractional Kelly Criterion:** Position sizing is not static. Sizing is governed by the Kelly equation, dynamically updated based on the historical win rate and payoff ratio of that specific algorithmic subset. To prevent blowups from Fat Tails, the system implements a strict *Fractional* Kelly (e.g., 0.25 Kelly max allocation).
