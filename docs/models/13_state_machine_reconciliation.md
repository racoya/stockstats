# Deep Dive: Order State Machine & Reconciliation

## 1. The Core Problem: Broken APIs & Orphaned Trades
Quantitative models (like GARCH or Cointegration) operate in a mathematically perfect vacuum where they assume: "If $Z > 2.0$, execute trade to buy 1 Bitcoin."

However, cryptocurrency exchanges and brokers are not perfect vacuums. Their APIs frequently suffer from:
1.  **Timeouts (HTTP 504 Gateway Timeout):** We send the `BUY` payload, but the exchange's matching engine is overloaded and we never receive a confirmation response.
2.  **Rate Limiting (HTTP 429 Too Many Requests):** We hit our API quota, and the execution is blocked.
3.  **Partial Fills:** We ordered 10 BTC, but only 2 BTC were available at our Limit price. The remaining 8 BTC sit open on the book as the price rockets away.

If our Execution Engine simply assumes a "Timeout" means the order failed, and it sends the `BUY` command *again*, we might accidentally double our exposure (purchasing 2 Bitcoin instead of 1) if the first order was actually processed by the exchange. This is catastrophic.

## 2. The Solution: The Deterministic State Machine
To guarantee the system never double-spends or loses track of capital, the STOCKSTATS Execution Engine physically decouples "Signal Generation" from "Order Execution." 

Execution is governed by a strict, one-way **Deterministic State Machine**.

### A. The Client Order ID (`clientOid`)
Every time the Logic Engine generates a signal, it creates a unique, cryptographically secure UUID (e.g., `ord-7f8a9b-11c2`). 
*   This UUID is saved into our local PostgreSQL immutable ledger *before* the order is sent to the exchange.
*   We inject this UUID into the exchange API payload as the `clientOid` (Client Order ID).

## 3. The Lifecycle States
An order can only exist in one of the following hard-coded statuses:

1.  `PENDING_SUBMIT`: The UUID is created in our DB, payload is actively in transit to the exchange API.
2.  `ACKNOWLEDGED`: The exchange WebSocket confirmed receipt of the `clientOid`, but it is not filled yet.
3.  `PARTIALLY_FILLED`: Execution has begun, but remaining quantity exists on the L2 book.
4.  `FILLED`: Complete execution. Transition to `POSITION_OPEN`.
5.  `CANCELED`: The order was deliberately killed by the SOR or VaR breach.
6.  `UNKNOWN`: **(The Danger State)**. A Timeout occurred. 

## 4. The Reconciliation Engine (Handling "UNKNOWN" States)
If a `PENDING_SUBMIT` order does not transition to `ACKNOWLEDGED` or `FILLED` within $N$ milliseconds, the system forces it into the `UNKNOWN` state.

**The Golden Rule:** The system is **HARD-LOCKED** from sending any new orders for that specific asset while an `UNKNOWN` state exists. It must enter Reconciliation Mode.

### The Reconciliation Protocol (Python)
1.  **Halt:** Pause all signal ingestion for the affected asset pair.
2.  **Query by UUID:** Send an explicit `GET /order?clientOid=ord-7f8a9b` request to the exchange.
3.  **Resolution Logic:**
    *   *If Exchange says "Order Not Found":* We mathematically prove the order died in transit. We mark our DB as `FAILED_TO_SUBMIT` and unlock the system to try again on the next signal.
    *   *If Exchange returns the Order Record:* We prove the order *did* execute. We pull the exact fill price and quantity, update our DB to `FILLED`, and resume normal operations.

```python
import asyncio
from typing import Dict

async def reconcile_unknown_order(exchange_api, client_order_id: str) -> Dict:
    """
    Halts the execution engine and interrogates the exchange API 
    to resolve a Timeout/Unknown state using the deterministic UUID.
    """
    max_retries = 3
    base_delay = 1.0 # Exponential backoff
    
    for attempt in range(max_retries):
        try:
            # Explicitly query by OUR generated UUID, not the exchange's ID
            order_status = await exchange_api.fetch_order(id=client_order_id, params={'clientOid': client_order_id})
            
            if order_status['status'] == 'closed':
                return {"resolution": "FILLED", "data": order_status['fills']}
            elif order_status['status'] == 'open':
                return {"resolution": "PENDING", "action": "CONTINUE_MONITORING"}
                
        except OrderNotFoundException:
            # The exchange never received our payload. Safe to retry next signal.
            return {"resolution": "DEAD_IN_TRANSIT", "action": "UNLOCK_SYSTEM"}
            
        except ExchangeTimeoutException:
            # The exchange is completely broken.
            await asyncio.sleep(base_delay * (2 ** attempt)) # 1s, 2s, 4s
            
    # If 3 retries fail, trigger Admin PagerDuty alert. Macro Kill Switch.
    return {"resolution": "CRITICAL_EXCHANGE_FAILURE", "action": "HALT_ALL_TRADING"}
```

By enforcing a strict State Machine mapped to deterministic UUIDs, we guarantee absolute parity between our internal PostgreSQL ledger and the exchange's matching engine, mathematically eliminating the "Zombie Order" double-spend risk.
