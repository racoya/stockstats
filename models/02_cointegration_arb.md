# Deep Dive: Cointegration & Statistical Arbitrage

## 1. The Flaw of Standard Correlation
When building a "Pairs Trading" or Statistical Arbitrage portfolio, amateur systems rely on **Pearson Correlation** ($\rho$). 

Correlation merely measures if two assets tend to move in the *same direction* over a period. However, two assets can be highly correlated while the absolute distance (the "spread") between their prices infinitely diverges. 
If you short Asset A and buy Asset B just because they are "highly correlated," and they structurally drift apart forever, the portfolio takes a 100% loss.

To trade the spread between two assets safely with an $R > 0$ expectancy, we must mathematically prove that the spread is **Stationary** (meaning it will always revert to a constant mean of zero). We do this via **Cointegration**.

## 2. The Cointegration Framework
Cointegration exists when a linear combination of two non-stationary time series (like the climbing prices of BTC and ETH) creates a completely stationary time series (their spread).

### Step 1: Calculate the Hedge Ratio ($\beta$) via OLS
We cannot simply subtract the price of Asset B from Asset A, as they have vastly different nominal values and volatility profiles. We must find the correct scaling factor (the Hedge Ratio, $\beta$).

We run an Ordinary Least Squares (OLS) regression between the two price arrays:
$$ Price_A = \alpha + \beta \times Price_B + \epsilon $$

*   *Output:* The $\beta$ coefficient tells us exactly how many units of Asset B we must buy/short to perfectly hedge 1 unit of Asset A.

### Step 2: Extract the Spread (The Residuals)
Now we isolate the residual error ($\epsilon$), which represents the Spread:
$$ Spread_t = Price_{A,t} - (\beta \times Price_{B,t}) $$

This $Spread_t$ array is what we will actually trade. 

### Step 3: The Augmented Dickey-Fuller (ADF) Test
This is the critical "Stop/Go" gate for the Quantitative Engine. We must prove the $Spread_t$ is stationary. We run the ADF test on the spread array.

*   **Null Hypothesis ($H_0$):** The spread has a "unit root" (it wanders randomly and will not mean-revert).
*   **Alternative Hypothesis ($H_1$):** The spread is stationary (it will reliably mean-revert).

If the ADF test returns a **p-value $\le 0.05$** (and the ADF test statistic is more negative than the critical value), we reject the Null Hypothesis. We now possess mathematical proof of cointegration.

## 3. Implementation in STOCKSTATS (The Logic Tree)

### Python Engine Logic
The system uses `statsmodels` to continuously evaluate asset pairs (e.g., BTC/ETH, or Coca-Cola/Pepsi).

```python
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# 1. Calculate Hedge Ratio via OLS
X = sm.add_constant(price_asset_B)
model = sm.OLS(price_asset_A, X).fit()
hedge_ratio_beta = model.params[1]

# 2. Calculate the Spread
spread = price_asset_A - (hedge_ratio_beta * price_asset_B)

# 3. Test for Stationarity 
adf_result = adfuller(spread)
p_value = adf_result[1]

if p_value <= 0.05:
    print("Pair is Cointegrated. Authorized for StatArb Engine.")
else:
    print("Spread is Random Walk. Veto Execution.")
```

### 4. The Execution Mandate (Z-Score)
Once a pair is proven cointegrated (p-value $< 0.05$), the Execution Engine converts the real-time spread into a normalized **Z-Score** to track how far it has deviated from its historical mean.

$$ Z\_Score = \frac{Spread_t - Mean(Spread)}{StdDev(Spread)} $$

*Note: The StdDev here should ideally be supplied by the GARCH model outlined in `01_garch_volatility.md`.*

*   **Entry Signal:** If $Z\_Score \ge +2.0$, the spread is abnormally wide. The system executes the $\beta$-adjusted short leg (Short A, Long B).
*   **Exit Signal:** When the $Z\_Score$ reverts to $0$ (the mean), both positions are closed simultaneously to capture the spread differential, completely immune to the overall macro market direction.
