# Strategy 03: The Mathematical Logic Engine

## 1. Objective
To formalize the quantitative principles, statistical boundaries, and execution logic that govern the STOCKSTATS $E(R) > 0$ intelligence mandate. 

The system operates strictly on verifiable, backtested mathematical formulas. Discretionary human trading intuition is mathematically banned from the logic engine.

> **CRITICAL DIRECTORY NOTE:** This strategy document serves as a high-level operational routing index. For the explicit Python code implementations, exact algebraic equations (SDEs, matrices), and Mermaid execution flowcharts of the core proprietary algorithms below, refer exclusively to the deep-dive whitepapers in the [`docs/models/` directory]():
> *   [00_model_index.md](../../docs/models/00_model_index.md) (The Master Index)
> *   [01_garch_volatility.md](../../docs/models/01_garch_volatility.md)
> *   [02_cointegration_arb.md](../../docs/models/02_cointegration_arb.md)
> *   [... and Models 03 through 15].

## 2. Phase I: Signal Generation (The Core Edge)
The core engine identifies pure statistical pricing anomalies. It must dynamically adjust to changing market environments to prevent entering trades against structural macro shifts.

### A. Dynamic Volatility ($\sigma$) via GARCH(1,1)
Static Standard Deviation algorithms fail catastrophically during "Fat Tail" events. The system implements a Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model.
*   **Purpose:** If the market experiences a sudden news event, the GARCH variance matrix instantly expands the $+/- 3\sigma$ trading envelope. This physically prevents the system from triggering a premature "Mean Reversion" buy order right as a market crash begins.
*   *See [Model 01](../../docs/models/01_garch_volatility.md)*

### B. Statistical Arbitrage (Cointegration)
The system analyzes the mathematical spread between two linked assets (e.g., BTC/ETH) rather than directional price guessing.
*   **Purpose:** Uses Eigenvalue Augmented Dickey-Fuller (ADF) tests to statistically prove the distance (spread) between two assets is "Stationary" (guaranteed to mean-revert) before authorizing a grid trade.
*   *See [Model 02](../../docs/models/02_cointegration_arb.md)*

### C. Market Regime Detection (Hidden Markov Models)
Mean-reversion algorithms will bankrupt a portfolio if executed during a strong directional macro breakout. 
*   **Purpose:** Utilizes Gaussian Hidden Markov Models (HMM) to autonomously classify the unobservable "State" of the market (e.g., Choppy vs. Trending) based on latent variance clustering, acting as a master VETO on opposing algorithms.
*   *See [Model 03](../../docs/models/03_hmm_regime_detection.md)*

## 3. Phase II: Signal Optimization (The Enhancers)
Once a signal generates, these models actively suppress legacy lag.

### A. Kalman Filters
*   **Purpose:** Replaces structural, lagging OLS moving averages. A recursive prediction/correction loop that calculates the true "hidden state" of the Hedge Ratio ($\beta$) tick-by-tick using standard Random Walk matrices.
*   *See [Model 07](../../docs/models/07_kalman_filters.md)*

### B. Fractional Differencing 
*   **Purpose:** Applies fractional binomial calculus to non-stationary price vectors. Achieves the strict stationarity required for Machine Learning ingestion while flawlessly preserving the long-term compounding memory that integer ($d=1$) differencing permanently destroys.
*   *See [Model 09](../../docs/models/09_fractional_differencing.md)*

## 4. Phase III: The Expectancy & Sizing Framework
The guiding principle of every algorithmic model is a mathematically proven positive edge ($E(R)$).

### A. The System Quality Number (SQN)
Every monetary trade outcome is structurally normalized to the Initial Risk ($1R$), completely removing arbitrary dollar amounts from the performance equation.
*   **Purpose:** Expectancy measures edge per trade. SQN calculates the reliability and statistical velocity of that edge against its own standard deviation. If a model generates a positive expectancy but an $SQN < 1.6$, it is algorithmically suppressed.
*   *See [Model 05](../../docs/models/05_expectancy_and_sqn.md)*

### B. Copulas & The Fractional Kelly Criterion
Position sizing is never static, and standard Pearson correlation ($\rho$) is rejected.
*   **Purpose:** The engine uses Clayton Copulas to model "Fat Tail" systemic crash dependencies between active assets. It sizes positions geometrically against the algorithm's historical Win Rate via the Fractional Kelly Criterion (e.g., $0.50f^*$) to guarantee the mathematical impossibility of portfolio ruin.
*   *See [Model 06](../../docs/models/06_copula_kelly_sizing.md)*

## 5. Phase IV: Validation & Defenses (The Shields)
Protecting the core logic engine from dirty data, false positives, and High-Frequency Trading predators.

### A. Machine Learning Overlays (Meta-Labeling)
*   **Purpose:** ML is not used to *discover* trades. It acts purely as a final veto filter. XGBoost classifiers analyze Triple-Barrier labeled historical features to assign a dynamic Probability of Success to the active linear signal, actively maximizing the F1-Score of the system.
*   *See [Model 10](../../docs/models/10_machine_learning_overlays.md)*

### B. Microstructure Toxicity Defenses (OBI & Hampel)
*   **Purpose:** Data ingested from WebSocket feeds must pass through high-frequency Numba-compiled Hampel Filters to scrub "rogue ticks." During execution, the system actively calculates the Order Book Imbalance (OBI) and VPIN flow ratio to pause Smart Order Routing if HFTs are actively "spoofing" our liquidity.
*   *See [Model 14](../../docs/models/14_data_scrubbing_hampel.md) & [Model 15](../../docs/models/15_orderbook_toxicity_obi.md)*
