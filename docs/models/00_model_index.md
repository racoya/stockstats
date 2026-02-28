# Mathematical Models Index: The Logic Engine

## Overview
This directory contains the deep-dive theoretical blueprints, mathematical equations, and Python implementation architecture for the core quantitative algorithms utilized by the STOCKSTATS platform. 

The models are strictly separated into fundamental operational domains, dictating the chronological flow of data from raw WebSockets down to localized execution algorithms.

## I. Signal Generation & Price Action (The Core Engine)
These models are responsible for discovering structural and temporal pricing anomalies in the primary exchange data.
*   **[01. Dynamic Volatility (GARCH)](01_garch_volatility.md):** Replaces static Standard Deviation. Uses Generalized Autoregressive Conditional Heteroskedasticity (GARCH 1,1) to instantly expand algorithmic execution bands during market shocks.
*   **[02. Cointegration & StatArb](02_cointegration_arb.md):** Replaces Pearson correlation. Utilizes Augmented Dickey-Fuller (ADF) Eigenvalue tests to mathematically prove the absolute spread between two assets is stationary (reliably mean-reverting) before authorizing grid trading.
*   **[03. Regime Detection (HMM)](03_hmm_regime_detection.md):** Uses Gaussian Hidden Markov Models and dynamic transition probability matrices to autonomously classify the macro market as "Choppy" or "Trending" based purely on latent variance clustering.

## II. Execution Mathematics & Capital Sizing (The Router)
These models dictate exactly *how* capital is deployed into a validated signal, maximizing geometric compounding while minimizing slippage.
*   **[04. VWAP & Liquidity Profiling](04_vwap_liquidity.md):** Maps historical 30-day liquidity arrays. Slices large parent orders into micro-orders via Volume-Weighted Average Price (VWAP) bounds to prevent sweeping the L2 order book (The 5% Participation Constraint).
*   **[05. Expectancy & System Quality (SQN)](05_expectancy_and_sqn.md):** Normalizes all physical trades to an Initial Risk multiplier ($R$). Calculates true mathematical Expected Value ($E(R)$) and structurally optimizes stop-losses via Maximum Adverse Excursion (MAE) grids.
*   **[06. Copulas & Fractional KellySizing](06_copula_kelly_sizing.md):** Employs Clayton Copula matrices to calculate "Fat Tail" systemic geometric crash dependencies between active assets. Sizes positions geometrically against the algorithm's Win Rate via the Fractional Kelly Criterion ($0.5f^*$).

## III. Statistical Filtering & Stationarity (The Enhancers)
Once a signal is generated, these models actively optimize the baseline parameters to eliminate temporal lag and predict capital lockup durations.
*   **[07. Kalman Filters](07_kalman_filters.md):** Replaces structural, lagging OLS moving averages. A recursive prediction/correction loop that calculates the true "hidden state" of the Hedge Ratio ($\beta$) tick-by-tick using standard Random Walk matrices.
*   **[08. Ornstein-Uhlenbeck (OU Process)](08_ornstein_uhlenbeck_halflife.md):** Calculates the continuous stochastic differential equation of mean reversion. Extracts the Half-Life ($\tau$) duration of a spread via AR(1) regression to veto trades that expose capital to massive borrowing rate lockups.
*   **[09. Fractional Differencing](09_fractional_differencing.md):** Applies fractional binomial calculus to non-stationary price vectors. Achieves strict stationarity required for ML models while flawlessly preserving the long-term compounding memory that integer ($d=1$) differencing destroys.

## IV. Validation & Portfolio Defenses (The Overlays)
These models serve as the master topological overlays and stress-testers to ensure the quantitative integrity of the entire Trading Desk.
*   **[10. Machine Learning Overlays (Meta-Labeling)](10_machine_learning_overlays.md):** Rejects end-to-end signal prediction. Employs non-linear XGBoost classifiers to output the probability of success for an *already-existing* baseline signal using Triple-Barrier Labels, dynamically suppressing false positives (F1-score sizing).
*   **[11. Backtesting Rigor & Statistical Deflation](11_backtesting_rigor_and_bias.md):** Mandates Point-in-Time data to eliminate survivorship/look-ahead bias, and utilizes the Deflated Sharpe Ratio (DSR) to calculate the $E[\max(SR)]$ hurdle, physically penalizing the system for data-mining and parameter overfitting.
*   **[12. Parametric Value at Risk (VaR)](12_value_at_risk_var.md):** The Master Kill Switch. Uses linear algebra to calculate the maximum potential dollar loss of the combined aggregated portfolio utilizing the dynamic GARCH variance-covariance matrix ($\Sigma$).

## V. Microstructure & API Realities (The Failsafes)
These specific protocols protect the perfectly sterile mathematical logic engines from the chaotic physical reality of broken server APIs and predatory liquidity makers.
*   **[13. Order State Machine & Reconciliation](13_state_machine_reconciliation.md):** Generates strictly deterministic UUIDs (`clientOid`) to force the Execution Engine to safely halt, query, and verify active L2 states during HTTP 504 exchange timeouts, structurally preventing double-spends.
*   **[14. Data Scrubbing & Hampel Filters](14_data_scrubbing_hampel.md):** The sterilization gate. Uses $O(N)$ high-frequency Numba-compiled Median Absolute Deviation (MAD) loops to instantly scrub glitchy "rogue" exchange ticks before they poison the upstream mathematical arrays.
*   **[15. Order Book Toxicity (OBI)](15_orderbook_toxicity_obi.md):** Defends against Adverse Selection and L2 "Spoofing" by HFTs. Calculates the localized Order Book Imbalance ratio and Maker/Taker VPIN arrays to instantly pause the VWAP Execution Slicer if the flow turns artificially toxic.
