# Sprint 3 Implementation: The Hampel Scrubber

## The Objective
In Sprint 2, we built the pipeline that physically pulls raw ticks from the exchange into our databases. However, raw exchange data is fundamentally dirty. Flash crashes, crossed order books, and API glitches inject "rogue" prices (e.g., Bitcoin suddenly trading at $0.05 for one microsecond).

If these rogue ticks make it into the TimescaleDB ledger, they will permanently corrupt the Phase 8 XGBoost Machine Learning models and cause our real-time GARCH arrays to trigger catastrophic false buys. 

Sprint 3 builds the physical **Median Absolute Deviation (MAD) Hampel Filter** to mathematically intercept and sanitize these ticks mid-flight.

**Reference:** [Model 14 (Hampel Filter)](../models/14_data_scrubbing_hampel.md)

---

## Step 1: The Matrix Initialization

The Hampel filter requires historical context. It cannot evaluate if a tick is "rogue" without knowing the consensus of the last $N$ ticks.

### 1.1 The Rolling Window Context
We will configure the Numba engine to maintain a rolling window (e.g., $N=50$ ticks) for each of our 50 assets simultaneously.
*   **The Fetch:** When the Ingestion loop starts, it makes one initial `SELECT` call to TimescaleDB to grab the last 50 ticks for `BTC/USDT` to seed the rolling array.
*   **The Memory:** These 50 ticks are held locally in the Python RAM as a Numpy `ndarray`.

## Step 2: The Core Mathematical Function (Numba JIT)

This is the most critical pipeline of the Phase 1 Scrubber. It runs on every single incoming trade. Pure Python is too slow, so we utilize the `@njit` decorator.

### 2.1 The Algorithm Code Block
Create `backend/core/hampel_filter.py`:

```python
import numpy as np
from numba import njit

@njit(cache=True)
def calculate_mad(rolling_window: np.ndarray) -> tuple[float, float]:
    """Calculates Median and Median Absolute Deviation using C-Level LLVM"""
    median = np.median(rolling_window)
    # MAD is the median of absolute deviations from the median
    deviations = np.abs(rolling_window - median)
    mad = np.median(deviations)
    return median, mad

@njit(cache=True)
def is_rogue_tick(current_price: float, median: float, mad: float, threshold: float = 3.0) -> bool:
    """Detects if price is X threshold MAD units away from the consensus median."""
    if mad == 0: 
        return False # Avoid division by zero if prices are perfectly flat
    
    # Calculate the Z-Score equivalent using MAD
    deviation = np.abs(current_price - median) / mad
    
    return deviation > threshold
```

## Step 3: The Interception Pipeline

We must inject the Numba functions directly between the CCXT WebSocket ingestion and the `asyncpg` insertion loops built in Sprint 2.

### 3.1 The Action Protocol
When a new tick arrives for `BTC/USDT` at $\$62,000$:

1.  **Calculate:** Pass the current 50-tick NumPy array for BTC to the `calculate_mad()` LLVM function.
2.  **Evaluate:** Pass the new $\$62,000$ price, the Median, and the MAD to `is_rogue_tick()`.
3.  **The Routing Decision:**
    *   *If `False` (Clean):* Proceed with standard Sprint 2 pipeline -> Insert into TimescaleDB -> Push to Redis Pub/Sub -> Append the $\$62,000$ to the end of the 50-tick Numpy array (popping the oldest tick).
    *   *If `True` (Rogue Glitch):* 
        *   **Do NOT** insert the $\$62,000$ into the permanent TimescaleDB ledger.
        *   **Do NOT** push the $\$62,000$ into Redis Pub/Sub (The GARCH engine must never see it).
        *   Instead, **Replace** the price with the calculated `median` of the rolling window. Log the event locally for auditing (`WARNING: Hampel filter triggered on BTC/USDT. Price $62,000 substituted with Median $64,200`), and process the sanitized median price down the pipeline.

---
**Next Step:** With the data now sterilized in real-time by the Hampel Scrubber and safely archived in Postgres and Redis, the structural Phase 1 Foundation is complete. We now physically construct the brain in **Sprint 4: The GARCH Volatility Engine**.
