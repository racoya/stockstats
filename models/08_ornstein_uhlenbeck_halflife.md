# Deep Dive: The Ornstein-Uhlenbeck (OU) Process & Mean-Reversion Half-Life

## 1. The Timing Problem in Mean Reversion
A Z-Score tells you *how far* a price or spread has drifted from its mean. Cointegration via ADF testing tells you that the spread *will eventually* revert to the mean.

Neither tells you **WHEN**. 

If a spread deviates by $3\sigma$, you might enter a Statistical Arbitrage trade. But if that specific spread mathematically takes an average of 6 months to mean-revert, the capital is locked up, accruing massive financing fees, and exposing the portfolio to severe opportunity cost and exogenous risk. In quantitative trading, time is risk.

To solve this, the engine must calculate the exact expected duration of the trade before authorizing entry. We achieve this using the **Ornstein-Uhlenbeck (OU) Process**.

## 2. The Ornstein-Uhlenbeck Process
The OU process is a continuous-time stochastic process that explicitly models the mathematics of mean reversion. It is the financial physics equation that describes a rubber band snapping back.

### The Stochastic Differential Equation
$$ dx_t = \theta (\mu - x_t) dt + \sigma dW_t $$

*   **$x_t$:** The current value of the spread.
*   **$\mu$:** The long-term mean of the spread.
*   **$(\mu - x_t)$:** The distance from the mean.
*   **$\theta$ (Theta - The Speed of Reversion):** The rate at which the spread decays back toward the mean. This is the holy grail metric.
*   **$\sigma dW_t$:** The random Brownian motion (noise/volatility) entering the system.

### Extracting the Half-Life
From the OU equation, we can isolate $\theta$ using an autoregressive $AR(1)$ regression on the spread. Once we have $\theta$, we can calculate the **Half-Life** of the mean reversion.

The half-life represents the expected time it takes for the spread to revert exactly halfway back to its mean.

$$ Half\_Life (t_{1/2}) = \frac{\ln(2)}{\theta} $$

## 3. Implementation in STOCKSTATS

### Calculating Theta ($\theta$) in Python
The logic engine runs an OLS regression of the spread's current value against its previous value to find the exact rate of decay.

```python
import numpy as np
import statsmodels.api as sm

def calculate_half_life(spread_array):
    # Calculate the change in the spread from t-1 to t
    spread_lag = spread_array.shift(1).fillna(method="bfill")
    spread_diff = spread_array - spread_lag
    
    # Add a constant (intercept)
    X = sm.add_constant(spread_lag)
    
    # Run OLS Regression: delta_Spread = Alpha + Theta * Spread_lag + Error
    model = sm.OLS(spread_diff, X).fit()
    
    # The slope is negative Theta (rate of decay)
    theta = -model.params[1]
    
    # If theta is negative or zero, it is NOT mean-reverting
    if theta <= 0:
        return np.inf
        
    # Calculate Half-Life
    half_life = np.log(2) / theta
    return half_life
```

### 4. The Execution Protocol (The Funding Veto)
The Half-Life calculation acts as a critical risk filter before the system routes an order.

*   **Parameters:** The user (or Admin) defines the strategy's maximum allowable time horizon (e.g., `Max_Trade_Duration = 4 Hours`).
*   **Logic Gate:** A $Z = 2.5$ signal triggers on the BTC/ETH spread. The ADF test confirms it is cointegrated. The system then calculates the OU Half-Life. 
    *   If $Half\_Life = 30$ minutes, the trade is authorized. It is a highly elastic, fast-snapping pair.
    *   If $Half\_Life = 72$ hours, the trade is **VETOED**. The capital lock-up and funding rates required to hold the trade until reversion mathematically destroy the Estimated Value ($E(R)$). 

By implementing the OU Process, the system formally quantifies the "Cost of Time."
