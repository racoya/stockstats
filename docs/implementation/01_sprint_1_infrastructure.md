# Sprint 1 Implementation: Core Infrastructure

## The Objective
Physically construct the Phase 1 Foundation of STOCKSTATS on the local machine. This involves scaffolding the isolated dual-database environment (TimescaleDB and Redis) and establishing the highly-controlled Python environment. 

**Prerequisites:** Docker Desktop and Python 3.11 installed locally.

---

## Step 1: Directory Scaffolding & Environment Variables
Before touching Docker or Python, we must build the physical directory structure to keep the repo clean and secure.

**1.1 Execute Terminal Commands:**
```bash
# Ensure you are in the root of the stockstats repository
mkdir -p backend/core backend/ingestion backend/execution backend/database
mkdir -p docker-volumes/timescaledb
mkdir -p docker-volumes/redis
```

**1.2 Create the `.env` Configuration:**
Create a file named `.env` at the root of the project. **Never commit this file.**
```env
# /stockstats/.env

# PostgreSQL / TimescaleDB Target
POSTGRES_USER=stockstats_admin
POSTGRES_PASSWORD=super_secure_dev_password_123!
POSTGRES_DB=stockstats
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379

# Execution Environment
STOCKSTATS_EXECUTION_MODE=SHADOW # Strict adherence to Phase 1 Rules
```

**1.3 Secure the Repository:**
Create or update `.gitignore` at the root:
```gitignore
# /stockstats/.gitignore
.env
venv/
__pycache__/
docker-volumes/
.DS_Store
```

---

## Step 2: The Dockerized Storage Layer
We isolate the databases in Docker to guarantee 1:1 parity with future production servers and prevent local OS corruption.

**2.1 Create `docker-compose.yml`:**
Create this file at the root of the project.
```yaml
# /stockstats/docker-compose.yml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb-ha:pg15-latest
    container_name: stockstats_timescaledb
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      # Map the physical host folder to the internal DB structure for persistence
      - ./docker-volumes/timescaledb:/home/postgres/pgdata/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: stockstats_redis
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - ./docker-volumes/redis:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
```

**2.2 Execute and Validate:**
Run the following terminal command to start the engine:
```bash
docker-compose up -d
```
*Validation:* Open DBeaver or TablePlus. Connect to `localhost:5432` using `stockstats_admin` and the password from your `.env`. Verify the connection is successful.

---

## Step 3: The Python Quantitative Core
We must isolate the mathematics engine dependencies flawlessly using a strict virtual environment.

**3.1 Initialize the Environment:**
```bash
python3.11 -m venv venv
source venv/bin/activate
# Your terminal prompt should now show (venv)
```

**3.2 Create the Dependency Freeze:**
Create `requirements.txt` in the root directory. Version locking is critical to prevent future package updates from breaking the Numba LLVM compiler.
```txt
# /stockstats/requirements.txt
ccxt[async]==4.2.35      # Async Exchange Websockets
numpy==1.26.4            # Array manipulation (Must match Numba requirements)
pandas==2.2.1            # Time-series DataFrames
numba==0.59.1            # LLVM Math Compiler for Hampel/GARCH
asyncpg==0.29.0          # Async PostgreSQL Driver (Fast Inserts)
redis==5.0.3             # Async Redis Pub/Sub
python-dotenv==1.0.1     # Environment variable injection
```

**3.3 Install Dependencies:**
```bash
pip install -r requirements.txt
```

---
**⬅️ Previous:** [Implementation Index](00_implementation_index.md) | **Next:** [Sprint 2: The Ingestion Gateway](02_sprint_2_ingestion_engine.md) ➡️
