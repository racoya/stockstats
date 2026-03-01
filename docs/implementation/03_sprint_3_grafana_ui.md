# Sprint 5 Implementation: Grafana Command Center & Manual Trading

## The Objective
We have sterile data entering the database (Sprint 1-3) and complex GARCH math generating upper/lower risk bounds in Python (Sprint 4). We now need to *see* it.

As established in [Strategy 10: Phase 3 Manual Trading](../strategy/10_phase_3_manual_trading.md), we are explicitly *not* building a bespoke Next.js UI yet. It is a massive engineering distraction. We will use Grafana connected directly to TimescaleDB as our Phase 1 "Command Center."

**Reference:** [Strategy 12 (Execution Sprints)](../strategy/12_execution_sprints_and_tickets.md#sprint-3-grafana-command-center--manual-trading)

---

## Step 1: Deploying the Grafana Docker Container

We inject Grafana directly into the local `docker-compose.yml` network alongside TimescaleDB.

**1.1 Update `docker-compose.yml` (Root Directory):**
Append the following service block to the file created in Sprint 1:

```yaml
  grafana:
    image: grafana/grafana-enterprise:latest
    container_name: stockstats_grafana
    # Important: Connect it to the same network as the database
    depends_on:
      - timescaledb
    ports:
      - "3000:3000"
    volumes:
      # Map the dashboards and configurations locally for persistence
      - ./docker-volumes/grafana:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    restart: unless-stopped
```

**1.2 Execute:**
Run `docker-compose up -d grafana` in the terminal to spawn the UI.

---

## Step 2: The PostgreSQL Data Source Connection

Grafana must read the underlying immutable ledger in real-time.

**2.1 Configuration:**
1. Navigate to `http://localhost:3000` in your browser.
2. Go to **Connections -> Add Data Source -> PostgreSQL**.
3. **Host:** `timescaledb:5432` *(Important: Use the internal Docker service name, not localhost)*.
4. **Database:** `stockstats`
5. **User:** `stockstats_admin` (From your `.env` file).
6. **Password:** `super_secure_dev_password_123!`
7. **TLS/SSL Mode:** `disable` (Localport to localport).
8. **TimescaleDB:** *Toggle the switch to ON* to enable time-series optimization.

---

## Step 3: Building the Visual "Flight Instruments"

We will build the primary Dashboard using SQL macros directly within Grafana.

### 3.1 The Time-Series L1 Chart (The Price Action)
Create a new Panel. Select **Time series** as the visualizer.

**The SQL Query:**
```sql
SELECT
  -- The $__timeGroup macro is essential for grouping massive ticks into readable candles (e.g., 1 minute)
  $__timeGroupAlias("time", $__interval),
  symbol AS metric,
  -- Calculate VWAP over the Grafana interval to prevent visual chart tearing
  SUM(price * volume) / SUM(volume) AS vwap_price
FROM raw_trades
WHERE
  $__timeFilter("time") AND symbol = 'BTC/USDT'
GROUP BY 1, 2
ORDER BY 1
```

### 3.2 The GARCH Volatility Bands (The Math Overlay)
*Note: This step requires a bridging table in PostgreSQL, as Sprint 4 currently publishes GARCH to Redis. You must modify Sprint 4 to optionally `INSERT` the completed GARCH bounds back into `timescaledb` if Grafana requires historical access to the bands.*

**The SQL Query (Assuming a `garch_bounds` table):**
```sql
SELECT
  time AS "time",
  upper_band,
  lower_band
FROM garch_bounds
WHERE
  $__timeFilter("time") AND symbol = 'BTC/USDT'
ORDER BY 1
```
*Action:* In the Graph settings, change the "Fill below to" property of `upper_band` to fill down to `lower_band`, creating a shaded volatility channel surrounding the raw price action.

---

## Step 4: The Alerting Webhook (Discord/Slack)

We do not sit and stare at Grafana all day. We use a Python script hooked to Discord to act as the "Tier 2 System Alert," ringing our phone when the GARCH signal triggers.

**4.1 Implement the Webhook (`backend/logic/alerts.py`):**
```python
import aiohttp
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

async def force_alert(symbol: str, price: float, lower_band: float):
    """Fires an HTTP POST request to Discord when a statistical anomaly is detected."""
    
    if price > lower_band: 
        return # Ignore. Price is safely inside the GARCH bands.

    message = {
        "content" : f"🚨 **STATISTICAL ANOMALY DETECTED** 🚨\n"
                    f"**Asset:** `{symbol}`\n"
                    f"**Current Price:** `${price}`\n"
                    f"**GARCH Lower Bound:** `${lower_band}`\n"
                    f"**Verdict:** Price is mathematically oversold based on rolling variance.\n"
                    f"*ACTION REQUIRED: Open Grafana Terminal to strictly verify HMM Regime logic.*"
    }

    async with aiohttp.ClientSession() as session:
        await session.post(DISCORD_WEBHOOK_URL, json=message)
```

---
**⬅️ Previous:** [Sprint 4: Quantitative Logic Engine](02_sprint_2_quantitative_logic_engine.md) | **Next:** [Sprint 6: Risk Matrices (Copula & Kelly)](04_sprint_4_risk_matrices.md) ➡️
