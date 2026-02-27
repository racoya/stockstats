# Mathematical Models: The Logic Engine Core

## 1. Objective
To formalize the mathematical principles, statistical boundaries, and execution logic that govern the $R > 0$ intelligence mandate. The system uses strict formulas, not discretionary feelings.

> **Note:** For specific Python implementation logic, equations, and code architecture of the core algorithms below, refer to the deep-dive whitepapers in the [`models/` directory](models/):
> *   [01_garch_volatility.md](models/01_garch_volatility.md)
> *   [02_cointegration_arb.md](models/02_cointegration_arb.md)
> *   [03_hmm_regime_detection.md](models/03_hmm_regime_detection.md)
> *   [04_vwap_liquidity.md](models/04_vwap_liquidity.md)
> *   [05_expectancy_and_sqn.md](models/05_expectancy_and_sqn.md)
> *   [06_copula_kelly_sizing.md](models/06_copula_kelly_sizing.md)

## 2. Dynamic Volatility & Mean Reversion
The core engine identifies statistical anomalies (deviation from the mean), but must dynamically adjust to changing market environments to prevent entering trades against structural macro shifts.

### A. The Baseline: Ordinary Least Squares (OLS)
The system calculates rolling linear regression to establish the dominant short-term trend ($m$) and the baseline mean.
*   **Equation:** $y_t = \alpha + \beta x_t + \epsilon_t$
    *   $\alpha$: Y-intercept
    *   $\beta$: The slope (momentum gradient). Trades are heavily penalized if the signal opposes the $\beta$ trajectory.
    *   $\epsilon_t$: The error term (residual).

### B. Dynamic Sigma ($\sigma$) Bands via GARCH(1,1)
Static Standard Deviation algorithms are dangerously slow to adapt to volatility shocks. The system implements a Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model to forecast conditional variance.
*   **Equation:** $\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$
    *   $\omega$: Baseline long-term variance.
    *   $\alpha$: Reaction to recent market shocks (the ARCH term).
    *   $\beta$: Persistence of volatility (the GARCH term).
*   **Logic:** If the market experiences a sudden news event (large $\epsilon_{t-1}^2$), the GARCH model instantly expands the $+/- 3\sigma$ condition, avoiding premature mean-reversion entries that a static model would blindly trigger.

## 3. Statistical Arbitrage & Cointegration
While core mean reversion applies to single assets, the "Statistical Arbitrage" mandate defined in the Project Vision requires analyzing the spread between two or more mathematically linked assets (e.g., BTC/ETH, or two correlated equities).

### A. Cointegration (Engle-Granger / Johansen Tests)
Standard correlation only measures directional similarity. Cointegration statistically proves that the distance (spread) between two assets is mean-reverting.
*   **The Spread Equation:** $Spread_t = AssetA_t - (\beta \times AssetB_t)$
    *   $\beta$: The hedge ratio (calculated via OLS regression between the two assets).
*   **Stationarity Testing:** The Logic Engine must run an **Augmented Dickey-Fuller (ADF)** test on the resulting $Spread_t$ time series.
*   **Logic:** If the ADF test yields a p-value $< 0.05$, the spread is mathematically "stationary" (proven to mean-revert). The system then generates a Long/Short signal when the $Spread_t$ diverges $\ge \pm 2\sigma$ from its mean.

## 4. Market Regime Detection
A mean-reversion strategy will suffer catastrophic losses if executed during a strong directional breakout regime. The system must autonomously identify the current macro state.

### A. Hidden Markov Models (HMM)
The logic engine utilizes Gaussian Hidden Markov Models to classify the unobservable "state" of the market based on observable emissions (returns and volatility).
*   **Regime Classifications (Hidden States):**
    1.  *State 0:* Low Volatility, Choppy/Ranging (Optimal for Mean Reversion execution)
    2.  *State 1:* High Volatility, Trending (Mean Reversion disabled, Momentum execution enabled)
    3.  *State 2:* Extreme Volatility, Crash (All systems to cash / Risk-Off)
*   **Logic:** Before authorizing any trade, the mathematical engine calculates the transition probability matrix to determine the most likely current $State$. If the system is in *State 1* (Trending), all opposing Mean Reversion $\sigma$-band signals are hard-vetoed.

## 5. Intraday Liquidity Mapping

### A. Volume-Weighted Average Price (VWAP) Normalization
The system cross-references real-time volume against historical intraday volume profiles.
*   **VWAP Equation:** $P_{VWAP} = \frac{\sum_j P_j \cdot Q_j}{\sum_j Q_j}$
*   **Logic:** Signals generated in low-liquidity zones (e.g., matching historical 20-minute periods accounting for $< 1\%$ of daily volume) are aggressively penalized. The order routing engine will automatically fraction the limit order size to prevent sweeping the order book and incurring excessive slippage.

## 6. The Expectancy Framework & System Quality
The guiding principle of every algorithmic model is a mathematically proven, positive edge over large sample sizes. To ensure this, the system relies on industry-standard quantitative nomenclature based around Initial Risk ($1R$).

### A. Position Sizing & The R-Multiple
Every trade outcome is normalized to the initial risk ($1R$) to evaluate pure signal edge, removing capital size from the performance equation.
*   **Initial Risk ($1R$):** $Entry\_Price - Stop\_Loss\_Price$
*   **Trade Outcome ($R-Multiple$):** $\frac{Net\_Profit}{1R\_Risk}$

### B. Mathematical Expectancy ($E$)
The system rejects raw win/loss dollar averages. The Logic Engine evaluates the underlying mathematical expectation using pure R-multiples.
*   **Net Profit calculation:** Friction must be deducted *per trade*, not averaged at the end.
    *   $Net\_Win = Gross\_Win - (Taker\_Fees + Maker\_Fees + Estimated\_Slippage + Spread)$
*   **Expectancy Formula:** $E(R) = (P_w \times \overline{W_R}) - (P_l \times \overline{L_R})$
    *   $P_w$: Probability of Winning (Win Rate)
    *   $\overline{W_R}$: Average Winning R-Multiple
    *   $P_l$: Probability of Losing (Loss Rate)
    *   $\overline{L_R}$: Average Losing R-Multiple (typically 1.0)
*   **Mandate:** The engine immediately disables any execution model where $E(R) \le 0.1$ factoring in friction.

### C. System Quality Number ($SQN$) & Trade Frequency
Expectancy measures edge per trade. SQN measures the reliability and velocity of that edge against its standard deviation.
*   **Formula:** $SQN = \frac{\sqrt{N} \times E(R)}{\sigma_R}$
    *   $N$: Number of trades in the sample (Velocity)
    *   $\sigma_R$: Standard Deviation of the R-multiples (Variance)
*   **Thresholds:** A system with a positive $E(R)$ but an $SQN < 1.6$ is deemed too volatile and will be suppressed.

### D. Trade Excursion Optimization (MAE / MFE)
To optimize the absolute $1R$ value, the system continuously audits historical trade paths.
*   **Maximum Adverse Excursion (MAE):** The maximum paper loss a trade experienced before closing as a win.
*   **Maximum Favorable Excursion (MFE):** The max paper profit reached before closing.
*   **Logic:** Continuous MAE analysis is fed into the regression loop to algorithmically tighten stop losses, technically increasing the R-multiple for the exact same market moves without changing the entry parameters.

## 7. Multi-Asset Correlation & Portfolio Sizing
To survive drawdowns, we mathematically distribute risk and protect capital dynamically.

### A. Copula Correlation Modeling (Tail Risk)
Standard Pearson correlation ($\rho$) fails during market crashes because all liquid risk assets tend to correlate to 1.0 simultaneously.
*   **Framework:** The system utilizes Copula functions (e.g., Clayton or Gumbel copulas) to model *joint tail dependency*.
*   **Logic:** Rather than asking "How correlated are Asset A and Asset B generally?", the algorithm calculates the specific mathematical probability that Asset A and Asset B will both suffer a $\ge -3\sigma$ crash block at the exact same time. Portfolio exposure is capped based on this tail risk dependency.

### B. The Fractional Kelly Criterion
Position sizing is never static. Sizing is governed by the Kelly equation, optimized continuously based on the historical win rate and payoff ratio of that specific algorithmic subset.
*   **Full Kelly Equation:** $f^* = \frac{p(b+1) - 1}{b}$
    *   $f^*$: The fraction of the portfolio to wager.
    *   $p$: The probability of a win (Win Rate).
    *   $b$: The ratio of the average win to the average loss (Payoff Ratio).
*   **Risk Constraint:** To prevent catastrophic blowups from "Fat Tails" (black swan events not captured in normal distribution), the system implements a strict **Fractional Kelly** mandate. The maximum allocation allowed out of the execution engine is hard-coded to a fraction (e.g., $0.25f^*$, or "Quarter Kelly").
