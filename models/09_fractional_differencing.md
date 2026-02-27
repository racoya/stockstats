# Deep Dive: Fractional Differencing & Memory Preservation

## 1. The Stationarity Dilemma in Machine Learning
As the STOCKSTATS system evolves toward Phase 3 (Full Autonomy), implementing predictive Machine Learning classification models (like Random Forests or Gradient Boosting) alongside the linear models becomes paramount. 

Machine Learning models in finance require input data to be **Stationary** (constant mean and variance over time). Feeding raw, trending price data ($Price_t$) to an ML model guarantees catastrophic failure because financial prices are non-stationary random walks.

### The Flaw of Integer Differencing
The standard industry fix to achieve stationarity is taking the first derivative—commonly known as working with "Returns" instead of "Prices".

$Return_t = Price_t - Price_{t-1}$

This is **Integer Differencing ($d=1$)**. While applying $d=1$ perfectly achieves stationarity, it **destroys all historical memory**. The series is completely stripped of its long-term momentum and structural trends. If you train an ML model solely on daily returns, it has absolutely no idea what the price was yesterday, last week, or last year. You have erased the sequence.

## 2. The Quantitative Solution: Fractional Differencing
Introduced to quantitative finance primarily by Dr. Marcos Lopez de Prado, **Fractional Differencing** solves this dilemma. 

Instead of differentiating by an integer ($d=0$ for prices, $d=1$ for returns), we differentiate by a fraction (e.g., $d=0.45$). We apply the absolute minimum amount of mathematical differencing required to *barely* pass the Augmented Dickey-Fuller (ADF) stationarity test, while preserving the maximum possible amount of original signal and historical memory.

### The Binomial Expansion
Fractional differencing utilizes the binomial series expansion to apply exponentially decaying weights to historical prices. Unlike $d=1$, which only looks at exactly 1 period ago $(-1 \times P_{t-1})$, $d=0.45$ looks at an infinite (or deeply truncated) window of past prices, with the weights asymptotically bleeding out to zero.

$$ (1-B)^d = \sum_{k=0}^{\infty} \binom{d}{k} (-B)^k = 1 - dB + \frac{d(d-1)}{2!}B^2 - \frac{d(d-1)(d-2)}{3!}B^3 \dots $$

*   $B$: The backshift operator ($B^k x_t = x_{t-k}$)
*   $d$: The fractional difference value.

### Iterative Weight Calculation
The exact mathematical weight assigned to the $k^{th}$ past price observation is calculated iteratively:
$$ w_k = -w_{k-1} \frac{d - k + 1}{k} $$

If $d = 0.45$:
*   Today's weight ($w_0$) = $1.0$
*   1 Day ago ($w_1$) = $-0.45$
*   2 Days ago ($w_2$) = $-0.123$
*   3 Days ago ($w_3$) = $-0.063$
*   *...and so on, preserving a mathematical tether back through time.*

## 3. Implementation in STOCKSTATS

### The Search for the Optimal $d$
The logic engine sweeps through potential values of $d$ (from $0.05$ up to $1.00$ in increments of $0.05$). For each $d$, it calculates the fractionally differenced series and runs an ADF test. The engine selects the lowest $d$ where the ADF test p-value drops $\le 0.05$.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def get_weights_ffd(d, threshold=1e-5):
    """Calculate the weights up to a designated threshold"""
    weights = [1.]
    k = 1
    while True:
        w_new = -weights[-1] * (d - k + 1) / k
        if abs(w_new) < threshold:
            break
        weights.append(w_new)
        k += 1
    return np.array(weights).reshape(-1, 1)

def frac_diff_ffd(series, d, threshold=1e-5):
    """Apply fractional differencing to a pandas series"""
    weights = get_weights_ffd(d, threshold)
    width = len(weights) - 1
    
    df = {}
    for name in series.columns:
        series_v = series[[name]].fillna(method='ffill').dropna()
        df_ = pd.Series(dtype=float)
        for iloc1 in range(width, series_v.shape[0]):
            loc0 = series_v.index[iloc1 - width]
            loc1 = series_v.index[iloc1]
            if not np.isfinite(series_v.loc[loc1, name]):
                continue
            # Apply the weights to the window
            df_.loc[loc1] = np.dot(weights.T, series_v.loc[loc0:loc1])[0, 0]
        df[name] = df_.copy(deep=True)
    df = pd.concat(df, axis=1)
    return df
```

### The Engineering Impact
When the time comes to train the system's Machine Learning regressors or classifiers (to act as confirmation filters for the baseline mathematical models), they will exclusively ingest **Fractionally Differenced features**. This guarantees mathematical soundness (stationarity) while allowing the ML engine to "see" the long-term momentum structures that integer differencing destroys.
