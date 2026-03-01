# Sprint 4 Implementation: The Quantitative Logic Engine

## The Objective
In Sprints 1-3, we built the physical infrastructure to ingest, scrub, and store raw exchange data. The data is now sterile and live.

Sprint 4 builds the brain: **The Quantitative Logic Engine**. This isolated microservice constantly polls the Redis sub-millisecond cache to calculate the $E(R)>0$ statistical edge. We prioritize the GARCH Volatility model first.

**Reference:** [Model 01 (GARCH Volatility)](../models/01_garch_volatility.md), [Strategy 12 (Execution Sprints)](../strategy/12_execution_sprints_and_tickets.md#sprint-2-the-quantitative-logic-engine-er0)

---

## Step 1: Microservice Scaffolding

We must separate the Logic Engine from the Ingestion Engine. If the math causes a CPU spike, it must not block the Websocket listener from receiving new trades.

**1.1 Scaffolding:**
Create `backend/logic/` and initialize the GARCH module.
```bash
mkdir -p backend/logic
touch backend/logic/main.py
touch backend/logic/garch_calculator.py
```

## Step 2: Subscribing to the Redis Event Bus

The Logic Engine does not constantly query the PostgreSQL SSD. It listens to the Redis Pub/Sub channel we built in Sprint 2.

**2.1 The Redis Listener (`backend/logic/main.py`):**
```python
import asyncio
import redis.asyncio as redis
from garch_calculator import process_garch_update
import os
from dotenv import load_dotenv

load_dotenv()

async def listen_to_ticks():
    """Connects to Redis and listens for new sterile ticks."""
    client = await redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)
    pubsub = client.pubsub()
    
    # Subscribe to all asset channels (e.g., tick:BTC/USDT)
    await pubsub.psubscribe("tick:*")
    
    print("Logic Engine: Listening for sterile ticks...")
    
    async for message in pubsub.listen():
        if message['type'] == 'pmessage':
            # Extract symbol and payload
            channel = message['channel']
            symbol = channel.split(":")[1]
            payload = message['data'] # Format: "timestamp|price|amount"
            
            # Fire the GARCH calculation asynchronously so we don't block the listener
            asyncio.create_task(process_garch_update(symbol, payload, client))

if __name__ == "__main__":
    asyncio.run(listen_to_ticks())
```

## Step 3: The GARCH Array mathematics (Numba JIT)

Standard `arch` library calls over 10,000 arrays per minute are drastically too slow for Python. We must build a recursive C-compiled array using Numba.

**3.1 Implement the Math (`backend/logic/garch_calculator.py`):**
```python
import numpy as np
import pandas as pd
from numba import njit
import json

# Global cache to prevent re-querying Redis for every single microsecond tick
# We only calculate the massive array once per N seconds
last_garch_calc_time = {}

@njit(cache=True)
def calculate_garch_variance(returns: np.ndarray, omega: float, alpha: float, beta: float) -> np.ndarray:
    """
    LLVM Compiled GARCH(1,1) Variance equation.
    var[t] = omega + alpha * return[t-1]^2 + beta * var[t-1]
    """
    T = len(returns)
    variance = np.zeros(T)
    # Seed the initial variance with the long-run sample variance
    variance[0] = np.var(returns) 
    
    for t in range(1, T):
        variance[t] = omega + alpha * (returns[t-1] ** 2) + beta * variance[t-1]
        
    return variance

async def process_garch_update(symbol: str, payload: str, redis_client):
    """Fetches the 5-minute rolling array from Redis and applies GARCH."""
    timestamp_str, price_str, _ = payload.split("|")
    current_time = int(timestamp_str)
    
    # Throttle mechanism: Only run heavy matrix math once every 5 seconds per asset
    last_calc = last_garch_calc_time.get(symbol, 0)
    if current_time - last_calc < 5000: # 5000 milliseconds
        return
        
    last_garch_calc_time[symbol] = current_time
    
    # 1. Fetch the sterile rolling array from Redis ZSET (Sprint 2)
    zset_key = f"cache:{symbol}"
    # Grab all ticks in the last 5 minutes
    cutoff_time = current_time - 300000 
    raw_ticks = await redis_client.zrangebyscore(zset_key, cutoff_time, current_time)
    
    if len(raw_ticks) < 100:
        return # Not enough data to form a statistical consensus
        
    # 2. Reconstruct the array
    prices = [float(tick.split("|")[1]) for tick in raw_ticks]
    price_array = np.array(prices)
    
    # 3. Calculate Log Returns
    # log_returns = ln(P_t / P_{t-1})
    returns = np.diff(np.log(price_array))
    
    # 4. GARCH Parameters (Hardcoded for MVP, dynamic fitting in Phase 8)
    # These must sum to < 1 for stationarity
    omega = 0.00001
    alpha = 0.05
    beta = 0.90
    
    # 5. Execute Numba C-Level Math
    variance_array = calculate_garch_variance(returns, omega, alpha, beta)
    current_variance = variance_array[-1]
    
    # 6. Calculate the Dynamic +/- 2 Sigma Bands
    # Standard Deviation is the square root of Variance
    current_std_dev = np.sqrt(current_variance)
    upper_band = price_array[-1] + (2 * current_std_dev * price_array[-1])
    lower_band = price_array[-1] - (2 * current_std_dev * price_array[-1])
    
    # 7. Publish the resulting bands back to Redis so Grafana/Execution can see them
    band_payload = json.dumps({
        "timestamp": current_time,
        "price": price_array[-1],
        "upper_band": upper_band,
        "lower_band": lower_band
    })
    await redis_client.publish(f"garch:{symbol}", band_payload)
    # Also save the latest value explicitly for the REST API
    await redis_client.set(f"latest_garch:{symbol}", band_payload)

```

---
**Sprint 4 Complete.** 
The Logic Engine is now entirely isolated from the Ingestion Engine. It listens to the Redis Pub/Sub stream, throttles itself to prevent CPU spikes, runs C-compiled GARCH volatility mathematics over the sterile arrays, and publishes the upper and lower dynamic bands back to the system.

In **[Sprint 5: Grafana & Manual Trading](05_sprint_5_grafana_ui.md)**, we will visually plot these bands and set up the Webhooks required for the Phase 1 founder to physically execute the signals.
