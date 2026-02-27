# Deep Dive: Kalman Filters & Dynamic Hedge Ratios

## 1. The Lag Problem with OLS Regression
In the `02_cointegration_arb.md` whitepaper, we use Ordinary Least Squares (OLS) regression to calculate the hedge ratio ($\beta$) between two assets. 

The critical flaw in OLS is that it is a **static, backward-looking** metric. OLS assumes the relationship between Asset A and Asset B is constant over the entire lookback window. In reality, financial relationships are highly dynamic. If you calculate an OLS $\beta$ over a 30-day window, a structural shift on Day 29 will barely move the $\beta$ value, leading to dramatically incorrect position sizing and a "broken" spread.

If we simply use a very short moving window (e.g., 2 hours) to calculate OLS, the model becomes overly sensitive to noise, causing the hedge ratio to whip violently back and forth.

## 2. The Solution: The Kalman Filter
The **Kalman Filter** is a recursive mathematical algorithm used extensively in aerospace (e.g., guiding Apollo rockets) and high-level quantitative finance. It dynamically estimates the true "hidden state" of a system (the true Hedge Ratio) from an ongoing stream of noisy observations (the price ticks).

Unlike OLS, the Kalman Filter updates its estimate of $\beta$ *tick-by-tick* without needing to recalculate the entire historical window. It assigns optimal mathematical weight to the new data tick versus the historical state.

### A. The Two-Step Recursive Process
The Kalman filter operates in a continuous loop of Prediction and Correction.

1.  **Prediction Step (Time Update):** 
    The model forecasts the expected state (the next $\beta$) and the uncertainty of that prediction (covariance prediction). Because we assume the true beta follows a random walk, the best prediction of tomorrow's $\beta$ is today's $\beta$.
    *   State Prediction: $\hat{x}_{k|k-1} = \hat{x}_{k-1|k-1}$
    *   Covariance Prediction: $P_{k|k-1} = P_{k-1|k-1} + Q$  *(where $Q$ is the process noise)*

2.  **Correction Step (Measurement Update):**
    When the new price tick arrives, the model calculates the error between the predicted price and actual price (the Innovation). It then calculates the **Kalman Gain ($K$)**—which mathematically decides whether to trust the *Prediction* more or the *New Measurement* more.
    *   Innovation: $\tilde{y}_k = z_k - H_k \hat{x}_{k|k-1}$
    *   Kalman Gain: $K_k = P_{k|k-1} H_k^T (H_k P_{k|k-1} H_k^T + R)^{-1}$  *(where $R$ is measurement noise)*
    *   State Update (The new $\beta$): $\hat{x}_{k|k} = \hat{x}_{k|k-1} + K_k \tilde{y}_k$

## 3. Implementation in STOCKSTATS

By utilizing the `pykalman` library, the logic engine abandons static OLS entirely for live execution.

### The Logic Engine Protocol
1.  **Initialization:** The algorithm seeds the initial state using a standard OLS regression over the first $N$ data points.
2.  **Tick-by-Tick Update:** As every new tick arrives, the Kalman Filter ingest the prices of Asset A and Asset B.
3.  **Output:** It outputs an instantaneously updated, optimally smoothed Hedge Ratio ($\beta_{dynamic}$) and intercept ($\alpha_{dynamic}$).

```python
from pykalman import KalmanFilter
import numpy as np

def update_dynamic_hedge_ratio(asset_x_prices, asset_y_prices):
    # Transition matrices for a random walk model
    delta = 1e-5
    trans_cov = delta / (1 - delta) * np.eye(2)
    
    # Initialize the Kalman Filter
    kf = KalmanFilter(
        n_dim_obs=1,
        n_dim_state=2,
        initial_state_mean=np.zeros(2),
        initial_state_covariance=np.ones((2, 2)),
        transition_matrices=np.eye(2),
        observation_matrices=np.expand_dims(np.vstack([[asset_x_prices], [np.ones(len(asset_x_prices))]]).T, axis=1),
        observation_covariance=1.0,
        transition_covariance=trans_cov
    )
    
    # Run the filter over the data stream
    state_means, _ = kf.filter(asset_y_prices.values)
    
    # Extract the dynamic Beta (Slope) and Alpha (Intercept)
    dynamic_betas = state_means[:, 0]
    return dynamic_betas[-1] # The real-time hedge ratio
```

### The Trading Impact
When a divergence occurs, the system utilizes the *exact* $\beta_{dynamic}$ calculated at that precise millisecond to calculate the Z-Score and size the short leg of the pair. This completely eliminates the lag and false signals inherent in rolling-window OLS moving averages.
