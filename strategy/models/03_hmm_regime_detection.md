# Deep Dive: Hidden Markov Models (Regime Detection)

## 1. The Death of Mean Reversion
A perfectly calibrated Mean Reversion algorithm (even one utilizing dynamic GARCH volatility bands) has a fatal mathematical flaw: **Macro Regime Shifts**.

If an asset is trading in a "Choppy/Ranging" environment (State 0), buying at the $-2\sigma$ band and selling at the mean is highly profitable. However, if macroeconomic news drops (e.g., unexpected inflation data), the market transitions into a "Trending/Breakout" environment (State 1).

In State 1, the price will blow through the $-2\sigma$ band, the $-3\sigma$ band, and the $-5\sigma$ band, trending downwards for weeks. If the system fails to recognize that the fundamental *state* of the market has changed, it will continuously buy the dips, averaging down into a catastrophic account liquidation.

We need a mathematical model that can determine what "Regime" the market is currently in, using only observable price action.

## 2. The Solution: Gaussian Hidden Markov Models (HMM)
A **Hidden Markov Model** is a statistical probabilistic model used to describe the evolution of observable events that depend on internal factors, which are not directly observable (hidden states).

*   **Observable Emissions:** The daily/hourly returns and the current volatility (GARCH).
*   **Hidden States:** The actual Market Regime (0: Ranging, 1: Bull Trend, 2: Bear Trend, 3: Crash).

### A. The Markov Property
The core assumption of HMM is the *Markov Property*, which states that the probability of transitioning to the next state depends *only* on the current state, completely ignoring all historical states prior to the current one. 

The market has no long-term memory; how it behaves in the next 5 minutes is entirely dictated by how it is behaving right now.

### B. The Transition Probability Matrix
The HMM calculates a matrix of probabilities ($\hat{P}$) showing the likelihood of moving from State $i$ to State $j$.

For a simple 2-State model (0: Ranging, 1: Trending):
$$
\begin{bmatrix}
P(0 \to 0) & P(0 \to 1) \\
P(1 \to 0) & P(1 \to 1) 
\end{bmatrix}
$$

If $P(1 \to 1)$ is $0.95$, it means once the market enters a Trend, there is a 95% probability it will *stay* in a Trend for the next time period.

## 3. Implementation in STOCKSTATS (The Logic Tree)

The Quantitative Engine runs the HMM asynchronously alongside the core pricing engine to act as the ultimate "Veto" switch.

### Step 1: Fitting the HMM (Python)
The engine utilizes the `hmmlearn` library, feeding it an array of recent returns and realized volatility to cluster the data into distinct Gaussian states.

```python
import numpy as np
from hmmlearn import hmm

# Define a 3-State Gaussian HMM
# State 0: Low Vol (Ranging)
# State 1: High Vol (Trending Up/Down)
# State 2: Extreme Vol (Crash/Panic)
model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000)

# X is a 2D array of [Returns, GARCH_Volatility]
model.fit(X_historical_data)

# Predict the current hidden state based on the most recent observations
current_hidden_state = model.predict(X_current_observation)[-1]
```

### Step 2: The Execution Protocol (The Veto)
The raw output of the HMM (`current_hidden_state`) must be mapped strictly to the execution risk profiles.

1.  **If `State == 0` (Ranging):**
    *   *Action:* Unleash the Mean Reversion sub-models. Authorize limit entries at GARCH $\pm 2\sigma$ bands.
2.  **If `State == 1` (Trending):**
    *   *Action:* **HARD VETO** all opposing Mean Reversion signals.
    *   *Alternative:* Activate Momentum sub-models (e.g., buying the breakout above OLS resistance).
3.  **If `State == 2` (Crash/Panic):**
    *   *Action:* Trigger Tier 1 Systemic Risk Protocol. Cancel all open passive limit orders immediately.

By using HMMs, STOCKSTATS achieves "Situational Awareness," ensuring it deploys the right mathematical model for the right market environment.
