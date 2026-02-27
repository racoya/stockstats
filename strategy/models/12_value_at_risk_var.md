# Deep Dive: Portfolio Value at Risk (VaR) & The Kill Switch

## 1. The Purpose of VaR
While the Fractional Kelly criterion ($f^*$) perfectly sizes individual positions based on their statistical edge, and Copulas measure the tail-correlation between two specific assets, we need a singular mathematical metric to govern the survival of the *entire* portfolio entity.

**Value at Risk (VaR)** answers the ultimate risk-management question:
*"Under normal market conditions, what is the maximum dollar amount this entire portfolio could lose over the next 24 hours with a 99% level of confidence?"*

If the calculated 99% VaR exceeds our hard-coded survival threshold, the system is deemed structurally unsafe, and the macro kill-switches must be engaged.

## 2. Parametric VaR Calculation (Variance-Covariance)
The STOCKSTATS system utilizes the Parametric (or Variance-Covariance) method for real-time VaR calculation, as it is computationally efficient and updates tick-by-tick.

### The Equation
To calculate the VaR of an N-asset portfolio:

$$ VaR_p = Z_{\alpha} \cdot \sqrt{w^T \cdot \Sigma \cdot w} \cdot Portfolio\_Value $$

### Deconstructing the Variables
*   **$Z_{\alpha}$:** The Z-score corresponding to our confidence interval. For a strict 99% confidence level, $Z \approx 2.33$.
*   **$w$:** A vertical vector (array) representing the percentage weights of all active positions in the portfolio.
*   **$w^T$:** The transpose (horizontal row) of the weights vector.
*   **$\Sigma$:** The Covariance Matrix of all assets currently held in the portfolio. *Crucially, STOCKSTATS dynamically feeds the output of the GARCH volatility models directly into this covariance matrix, ensuring VaR expands immediately during a market shock.*
*   **$\sqrt{w^T \cdot \Sigma \cdot w}$:** This matrix multiplication yields the total standard deviation ($\sigma_p$) of the combined portfolio, explicitly accounting for the diversification (or lack thereof) between the assets.

## 3. Implementation in STOCKSTATS

### Real-Time Python Calculation
The Risk Engine microservice continuously polls the live portfolio balances and the real-time GARCH covariance matrix.

```python
import numpy as np
import scipy.stats as stats

def calculate_portfolio_var(portfolio_value, weights_array, covariance_matrix, confidence_level=0.99):
    """
    Calculates the 1-Day Value at Risk for the entire active portfolio.
    """
    # 1. Get the Z-Score for the 99% confidence interval (approx 2.33)
    z_score = stats.norm.ppf(confidence_level)
    
    # 2. Calculate Portfolio Variance via matrix multiplication (w^T * Sigma * w)
    portfolio_variance = np.dot(weights_array.T, np.dot(covariance_matrix, weights_array))
    
    # 3. Calculate Portfolio Standard Deviation (Volatility)
    portfolio_std_dev = np.sqrt(portfolio_variance)
    
    # 4. Calculate Absolute VaR
    var_dollar_amount = portfolio_value * portfolio_std_dev * z_score
    
    return var_dollar_amount
```

### 4. The Macro Execution Matrix (The Master Kill Switch)
The output of the VaR calculation governs the global state of the entire Trading Desk. 

Assume the mandate dictates that the fund cannot mathematically risk losing more than 5% of its total NAV in a single day.

*   **State Green (VaR $\le 3\%$ of NAV):** 
    All quantitative engines are authorized. New signals are parsed and routed to execution.
*   **State Amber (VaR $3.1\% - 4.9\%$ of NAV):** 
    *Risk-Reduction Mode.* The execution engine is physically disconnected from entering *new* positions. It is only authorized to route market/limit orders that reduce existing exposure or close open trades.
*   **State Red (VaR $\ge 5\%$ of NAV):** 
    *Systemic Breach.* 
    1. The `hmmlearn` Regime Detection flags State 2 (Crash).
    2. The VaR breach confirms portfolio toxicity.
    3. The Master Kill Switch is engaged. All open limit orders are cancelled. Active positions may be aggressively flattened via TWAP execution to cash depending on Admin settings. The APIs are locked until manual human intervention.
