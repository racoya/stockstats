# Sprint 3 Implementation: The Hampel Scrubber

## The Objective
In Sprint 2, we built the pipeline that physically pulls raw ticks from the exchange. However, raw exchange data is fundamentally dirty. Flash crashes, crossed order books, and API glitches inject "rogue" prices. 

Sprint 3 builds the physical **Median Absolute Deviation (MAD) Hampel Filter** to mathematically intercept and sanitize these ticks mid-flight *before* they hit the TimescaleDB ledger.

**Reference:** [Model 14 (Hampel Filter)](../models/14_data_scrubbing_hampel.md)

---

## Step 1: The Core Mathematical Function (Numba JIT)

Pure Python is too slow to calculate rolling medians on every incoming microsecond tick. We utilize the `@njit` (No Python JIT) decorator to compile the math down to C-level machine code via LLVM.

**1.1 Create `backend/core/hampel_filter.py`:**
```python
# backend/core/hampel_filter.py
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

---

## Step 2: The Rolling Window Context Matrix

The Hampel filter requires memory. It cannot evaluate a tick without knowing the consensus of the last 50 ticks.

**2.1 Create the Context Manager in `backend/ingestion/stream.py`:**
```python
# Add to backend/ingestion/stream.py

import numpy as np
from core.hampel_filter import calculate_mad, is_rogue_tick

# Global state to hold the last 50 prices for each active symbol
rolling_windows = {}

async def initialize_rolling_windows(symbols: list, pg_pool):
    """Fetches the last 50 physical trades from TimescaleDB on startup."""
    async with pg_pool.acquire() as connection:
        for symbol in symbols:
            # Query the DB to seed the Numpy array
            records = await connection.fetch('''
                SELECT price FROM raw_trades 
                WHERE symbol = $1 
                ORDER BY time DESC LIMIT 50
            ''', symbol)
            
            prices = [r['price'] for r in records]
            # Reverse to chronological order and convert to C-contiguous Numpy array
            rolling_windows[symbol] = np.array(prices[::-1], dtype=np.float64)
```

---

## Step 3: The Interception Pipeline

We must inject the Numba functions directly between the VWAP Aggregator and the Database Router inside `process_tick`.

**3.1 Update `process_tick` in `stream.py`:**
```python
# Inside backend/ingestion/stream.py

async def process_tick(trade: dict, pg_pool, redis_client):
    # ... (Sprint 2 Microsecond VWAP Aggregation Logic happens here) ...
    
    # Let's assume the coalesced tick is ready:
    coalesced_tick = tick_buffer[dict_key]
    symbol = coalesced_tick['symbol']
    price = coalesced_tick['price']
    
    # THE HAMPEL INTERCEPTION
    window = rolling_windows.get(symbol)
    if window is not None and len(window) == 50:
        median, mad = calculate_mad(window)
        
        if is_rogue_tick(price, median, mad, threshold=3.0):
            logging.warning(f"ROGUE TICK DETECTED on {symbol}: ${price}. Substituting with Median ${median}")
            # Sanitize the tick
            coalesced_tick['price'] = float(median)
            # Do NOT update the rolling window with the bad price.
        else:
            # Clean tick. Update the rolling window (pop oldest, append newest)
            rolling_windows[symbol] = np.roll(window, -1)
            rolling_windows[symbol][-1] = price

    # Proceed to flush the (now strictly sanitized) tick to Postgres and Redis
    asyncio.create_task(route_to_databases(coalesced_tick, pg_pool, redis_client))
```

---
**⬅️ Previous:** [Sprint 2: The Ingestion Gateway](02_sprint_2_ingestion_engine.md) | **Next:** [Sprint 4: The Quantitative Logic Engine](04_sprint_4_quantitative_logic.md) ➡️
