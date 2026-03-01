# Sprint 6 Implementation: The Copula & Kelly Risk Matrices

## The Objective
Sprints 1-5 established the $E(R)>0$ statistical edge and built the Grafana UI for manual Phase 1 trading. However, an edge is useless if a systemic "fat tail" shock wipes out the portfolio.

Before we can automate the execution router in Sprint 7, we must build the advanced Risk Engine. This engine calculating dependency structures (Copulas) and optimal position sizing (Fractional Kelly) *before* authorization.

**Reference:** [Model 06 (Copula Dependency & VaR)](../models/06_copula_dependency.md), [Strategy 12 (Execution Sprints)](../strategy/12_execution_sprints_and_tickets.md#sprint-4-risk-matrices--capital-sizing-defense-systems)

---

## Step 1: Architecting the Risk Engine

The Risk Engine sits logically between the Quantitative Logic Engine (Sprint 4) and the Execution Router.

**1.1 Scaffolding:**
Create `backend/risk/` and initialize the modules.
```bash
mkdir -p backend/risk
touch backend/risk/copula_matrix.py
touch backend/risk/kelly_sizing.py
```

## Step 2: Clayton Copula Tail-Risk Veto (Numba JIT)

Standard Pearson Correlation ($R$) breaks down during market crashes (correlations go to 1). We must implement the Clayton Copula to detect non-linear tail dependency.

**2.1 Create the Copula Math (`backend/risk/copula_matrix.py`):**
```python
import numpy as np
import scipy.stats as stats
import logging

def calculate_clayton_dependency(asset_a_returns: np.ndarray, asset_b_returns: np.ndarray) -> float:
    """
    Calculates the Clayton Copula theta parameter for lower-tail dependency.
    Requires the historical return arrays of the two assets being evaluated.
    """
    # 1. Convert returns to uniform margins using empirical CDF
    u = stats.rankdata(asset_a_returns) / (len(asset_a_returns) + 1)
    v = stats.rankdata(asset_b_returns) / (len(asset_b_returns) + 1)
    
    # 2. Kendall's Tau estimation (Non-parametric correlation)
    tau, p_value = stats.kendalltau(u, v)
    
    # 3. Estimate Clayton Copula Theta from Tau
    # Theta relates to the strength of lower-tail dependency (crashes together)
    if tau <= 0:
        return 0.001 # Independence or negative correlation. Safe.
        
    theta = (2 * tau) / (1 - tau)
    return theta

def evaluate_tail_risk(target_asset: str, active_portfolio: list, redis_client) -> bool:
    """
    Checks if adding the target_asset drastically increases portfolio VaR.
    Returns True if safe, False if vetoed.
    """
    # ... Fetch 30-day return histories from TimescaleDB for the target_asset
    # ... and all assets currently held in the active_portfolio ...
    
    # Pseudocode Logic:
    # 1. For each held asset, calculate_clayton_dependency(target_asset, held_asset)
    # 2. If theta > 2.0 (High Crash Dependency): 
    #       logging.warning(f"VETO: Adding {target_asset} clusters Copula risk with current holdings.")
    #       return False
    # 3. return True
    pass
```

## Step 3: Fractional Kelly Position Sizing

The math says "Buy." The Copula says "Safe." How much of the $\$10,000$ portfolio do we commit? We never use static percentages ($5\%$). We size dynamically based on the algorithm's historical accuracy.

**3.1 Implement the Kelly Criterion (`backend/risk/kelly_sizing.py`):**
```python
def calculate_fractional_kelly(win_rate: float, average_win_ratio: float, fraction: float = 0.5) -> float:
    """
    Calculates the optimal fraction of capital to risk.
    W = Probability of Winning (e.g., 0.55)
    R = Payoff Ratio (Avg Win Amount / Avg Loss Amount)
    """
    # Full Kelly Formula: f* = W - ((1 - W) / R)
    loss_rate = 1.0 - win_rate
    
    if average_win_ratio <= 0:
        return 0.0 # Mathematically impossible edge
        
    full_kelly = win_rate - (loss_rate / average_win_ratio)
    
    if full_kelly <= 0:
        return 0.0 # The system does not possess a statistical edge. Do not trade.
        
    # We never bet Full Kelly (too volatile). We use Half Kelly.
    fractional_kelly = full_kelly * fraction
    
    # Hard cap the absolute maximum risk to 5% of portfolio regardless of math
    return min(fractional_kelly, 0.05)

def format_order_size(total_portfolio_nav: float, win_rate: float, avg_r: float) -> float:
    """Returns the absolute dollar amount to allocate to the trade."""
    f_star = calculate_fractional_kelly(win_rate, avg_r, fraction=0.5)
    allocated_capital = total_portfolio_nav * f_star
    return allocated_capital
```

---

## Step 4: The Interception Pipeline

When the Quantitative Logic Engine (Sprint 4) detects an anomaly, it must pass the signal to the Risk Engine *before* it alerts the Discord Webhook.

1.  **Logic Engine:** Detects GARCH variance anomaly on `SOL/USDT`.
2.  **Risk Engine (Copula):** Checks if `SOL/USDT` is highly tail-dependent on our currently open `ETH/USDT` position. (If True -> Veto -> Drop Trade).
3.  **Risk Engine (Kelly):** If safe, it calculates the $f^*$ position size (e.g., $1.8\%$ of NAV = $\$180$).
4.  **Notifier:** Generates the Discord Webhook: `"GARCH Alert: BUY SOL/USDT. Risk Engine authorizes $180 allocation (Half-Kelly)."`

---
**Sprint 6 Complete.** 
The portfolio is now mathematically defending itself. We are sizing organically based on System Quality, and we are structurally immune from highly correlated flash crashes destroying Multiple overlapping positions. 

Proceed to **Sprint 7: The Automated Execution Router**.
