# Sprint 1 Implementation: Infrastructure & DevOps

## The Objective
Before a single line of quantitative mathematics is written, we must pour the concrete foundation. This Master Sprint Document defines the exact physical servers, the remote collaboration environments, the CI/CD pipelines, and the physical directory scaffolding required to host STOCKSTATS.

This document consolidates six distinct architectural pillars:
1.  **Hardware Sizing:** What physical machines run the code.
2.  **Environment Isolation:** 12-Factor App methodology for Dev/Staging/Prod.
3.  **Remote Collaboration:** Tailscale VPN and VS Code Remote environments.
4.  **Git Workflows:** Trunk-Based Development and Code Reviews.
5.  **AI Integration:** How humans and Agents collaborate.
6.  **Core Scaffolding:** Building TimescaleDB, Redis, and Python locally.

---

## Pillar 1: Hardware & Infrastructure Sizing Matrix

As we transition from theory to execution, the physical machines running the STOCKSTATS codebase must scale alongside the software phases. The foundational requirement across all machines is **Ubuntu Server 24.04 LTS**. We do not deploy production code on Windows or macOS.

### 1.1 Sprints 1-5: The Phase 1 MVP (Centralized Basement Server)
We prioritize cost and iteration speed. Instead of developers working in silos on laptops, we utilize a **Centralized Basement Server** (DevBox & Data Hub) from Day 1.

*   **Bare-Metal vs. Hypervisor:** The STOCKSTATS Ubuntu OS does *not* need to be the only operating system on the physical hardware. It is actively encouraged to run as a **Dedicated Virtual Machine** (via Proxmox, ESXi, or Hyper-V) alongside your existing basement VMs, provided it is treated as a tier-one citizen.
*   **Persistent Data Ingestion:** The server runs TimescaleDB 24/7. This guarantees an unbroken dataset of L1 ticks.
*   **VS Code Remote Development:** Developers write code directly on the server's compute cycles via SSH.

**Minimum Hardware Specifications (Allocated to the VM):**
*   **CPU:** 8+ Dedicated vCores (e.g., pinned from an Intel i7/i9 or AMD Ryzen). Simulates execution loops and handles simultaneous SSH sessions without thread blocking. Do not over-provision these cores to other VMs.
*   **RAM:** 32-64 GB (ECC Preferred). TimescaleDB and Pandas matrices consume massive memory. Out-Of-Memory (OOM) kills during a live trade are catastrophic. The Hypervisor must *lock* this memory to the STOCKSTATS VM (no ballooning).
*   **Storage:** 1 TB NVMe SSD (PCIe Gen 4.0+). Mechanical HDDs or SATA SSDs are strictly prohibited. The Hypervisor must configure the drive for direct hardware passthrough (e.g., PCI Passthrough or raw ZFS block devices) to ensure the VM has unrestricted access to the $5,000+$ IOPS necessary to prevent database queuing.
*   **Network:** Stable 500+ Mbps Fiber connection. 

### 1.2 Sprints 6-9: Autonomous Execution (Production Deployment)
For the foreseeable future, **Production will run alongside Development on the Basement Server**. A strong local server can handle both workloads brilliantly, provided they are heavily guarded by strict Docker boundaries.

*   **Machine Type:** The existing Centralized Basement Server.
*   **The Docker Mandate:** Production logic does *not* execute natively. It runs inside a locked Linux Docker Container (`stockstats-prod-engine`). If the dev team crashes the system with a memory leak during testing, Docker `cgroup` limits guarantee the Production Engine remains unaffected.
*   **Future Note on Latency Arbitrage:** In Phase 9, when sub-millisecond latency becomes a limiting factor, we can migrate the `stockstats-prod-engine` Docker container to an AWS ECS cluster in Tokyo (`ap-northeast-1`). Until then, domestic network latency is acceptable for our macroscopic $E(R)>0$ edge.

### 1.3 Sprint 10: Machine Learning (GPU Acceleration)
Compiling XGBoost gradient trees across 100 boosting rounds is computationally massive for standard CPUs. However, if the Basement Server has a high-end dedicated GPU (e.g., NVIDIA RTX 3090 / 4090), we do not need AWS Cloud.

*   **GPU:** The local NVIDIA card inside the Basement Server running CUDA toolkits.
*   **Cost Strategy:** Zero marginal cost. We train the trees locally, save the `meta_model.json`, and pass it locally to the Production Container.

---

## Pillar 2: Environment Management & CI/CD

An algorithmic trading machine with direct API access to live retirement accounts cannot be tested "in production." To ensure absolute reproducibility, security, and portability across local and cloud environments, STOCKSTATS rigorously adheres to the **12-Factor App Methodology**.

### 2.0 The 12-Factor Mandate

Before deploying any logic, engineers must comply with these non-negotiable architectural constraints for our Python microservices:

```mermaid
graph TD
    classDef factor fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef core fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    
    A[STOCKSTATS Repo]:::core --> B(I. Codebase:<br/>One logic repo, multiple deployed targets)
    B --> C(II. Dependencies:<br/>Strict 'requirements.txt' isolation)
    C --> D(III. Configuration:<br/>Secrets injected via '.env' only)
    D --> E(IV. Backing Services:<br/>TimescaleDB/Redis treated as attached URLs)
    E --> F(V. Build, Release, Run:<br/>Immutable Docker deployments)
    F --> G(X. Dev/Prod Parity:<br/>Identical OS environments via Docker)
```

**Core Adoptions for STOCKSTATS:**
*   **I. Codebase:** We maintain a single Git repository (`origin/main`). The *exact same Python code* runs in Dev, Staging, and Production.
*   **II. Dependencies:** All Python quantitative libraries (Numba, Pandas) are explicitly declared and locked in `requirements.txt`. There is zero implicit reliance on Ubuntu OS-level packages.
*   **III. Configuration (The Golden Rule):** Binance Trading API keys, `JWT` token salts, and TimescaleDB passwords are **systematically prohibited** from entering the codebase. They must be injected into the Docker containers at execution time via local `.env` bindings.
*   **IV. Backing Services:** TimescaleDB and Redis are treated as loosely coupled attached resources. If the database physical IP changes (e.g., migrating to AWS RDS), the Python codebase does not change; only the `.env` target URL changes.
*   **X. Dev/Prod Parity:** We violently minimize the gap between environments. Development, Staging, and Production operate on the exact same Linux distributions driven by Docker Compose.

### 2.1 The Three Isolated Environments (Single Physical Host / VM)
Because all three stacks live on the identical Basement Server initially, we achieve isolation entirely through **Docker Networking** and **Port Mapping**. They must never share a database instance.

1.  **🟢 Development (DEV):** 
    *   **Architecture:** Runs natively via VS Code remote (`python3 ingest.py`). Connects to `localhost:5432` (Dev Timescale).
    *   **Keys:** Binance Testnet or Read-Only Mainnet keys.
    *   **Execution:** Mathematically blocked. `STOCKSTATS_EXECUTION_MODE=SHADOW`
2.  **🟡 Staging / Paper Trading (UAT):** 
    *   **Architecture:** Runs inside a Docker Container (`stockstats-staging`). Connects to an isolated `localhost:5433` (Staging Timescale).
    *   **Goal:** Forward-testing over 30 days. Uses Read-Only Mainnet Keys. Trades route exclusively to the local SQL `shadow_execution_ledger` to statistically verify slippage without risking physical capital.
3.  **🔴 Production (PROD):** 
    *   **Architecture:** Runs completely headless inside an isolated Docker Container (`stockstats-prod`). Connects to an incredibly secure `localhost:5434` (Prod Timescale bindings limited exclusively to the Docker Bridge).
    *   **Keys:** Binance Mainnet TRADING Keys (Withdrawals physically disabled at exchange level).
    *   **Execution:** Fully Live. `STOCKSTATS_EXECUTION_MODE=LIVE`

### 2.2 Continuous Integration & Deployment (CI/CD) Pipeline
We deploy via an immutable, automated pipeline. Humans do not manually SSH into the server to `git pull` the Production container.

```mermaid
sequenceDiagram
    participant Dev as Developer MacBook
    participant GH as GitHub (Origin)
    participant CI as GitHub Actions
    participant Prod as Basement Server

    Dev->>GH: 1. Push Feature Branch
    Dev->>GH: 2. Open Pull Request (PR)
    GH->>CI: 3. Trigger CI Pipeline
    activate CI
    CI-->>CI: Run Flake8 (Syntax Linting)
    CI-->>CI: Run PyTest (Mathematical Validation)
    CI-->>GH: 4. Pass / Fail Status
    deactivate CI
    GH->>GH: 5. Peer Review & Squash Merge
    GH->>Prod: 6. Webhook Trigger CD Script
    activate Prod
    Prod-->>Prod: git pull origin main
    Prod-->>Prod: docker-compose build stockstats-prod
    Prod-->>Prod: docker-compose up -d --no-deps stockstats-prod
    deactivate Prod
```

*   **CI (Testing):** Before merging to `main`, GitHub Actions runs `flake8`, `black`, and `pytest`. If mathematical validation fails (e.g., the Hampel filter returns the wrong MAD on a mock array), GitHub physically blocks the "Merge" button.
*   **CD (Deployment):** Merging an approved PR into `main` fires a secure webhook to the Basement Server, triggering a bash script to pull the code, rebuild the Production Docker image, and hot-swap the internal container without dropping active websocket connections.

---

## Pillar 3: Remote Development Environment (Zero-Trust)

This section mandates the rigorous cryptographic protocols for remote team access to the Basement Server. We operate under a Zero-Trust architecture.

### 3.1 Network & User Isolation Strategy
The Basement Server has absolutely **no open public ports**. All ingress is blocked at the firewall level.

```mermaid
graph LR
    subgraph Tailscale Encrypted Intranet
        Mac[Developer MacBook<br/>Tailscale IP: 100.x.y.z]
        Server[Basement Server<br/>Tailscale IP: 100.a.b.c]
    end
    Internet((Public Internet))
    
    Mac -- WireGuard Encrypted Tunnel --> Server
    Internet -.-x|Blocked by UFW Firewall| Server
```

1.  **Tailscale VPN:** Install Tailscale on the Ubuntu Server (`sudo tailscale up`) and all developer hardware.
2.  **User Provisioning:** The physical `root` account is permanently disabled for SSH. Create isolated Linux profiles dynamically: 
    ```bash
    sudo adduser dev_alice
    sudo usermod -aG sudo dev_alice
    sudo usermod -aG docker dev_alice
    ```
3.  **Cryptographic SSH Keys:** Password authentication is strictly disabled (`PasswordAuthentication no` in `sshd_config`). Developers must generate modern Elliptic Curve keys (`ssh-keygen -t ed25519`). Legacy RSA keys are prohibited. The Admin injects the `id_ed25519.pub` into `/home/dev_alice/.ssh/authorized_keys`.

### 3.2 The VS Code Remote-SSH Workflow
Remote developers compile Python directly on the Basement Server's CPU, avoiding local MacBook dependency bloat.
1.  Install the **Remote - SSH** extension in Visual Studio Code.
2.  Add the Host to `~/.ssh/config` using the Tailscale 100.X IP and the specific `User dev_alice`.
3.  Connect to Host -> Open Folder `/opt/stockstats/`. (The repository namespace rigidly employs `chmod 775` group permissions allowing multi-developer collaboration).
4.  Non-developer Traders simply open Chrome and navigate to `http://<tailscale-ip>:3000` over the VPN to view live Grafana surveillance panels securely.

---

## Pillar 4: Git & GitHub Collaboration Workflows

To maintain a mathematically pristine and auditable codebase across a distributed quantitative team, we enforce strict **Trunk-Based Development** paired with **Conventional Commits** and rigid Pull Request (PR) templates. This is an industry-standard mandate.

### 4.1 Branch Naming Conventions
Every ticket generated from the [Execution Sprints](../strategy/12_execution_sprints_and_tickets.md) becomes an isolated, short-lived branch. Branches must live $< 48$ hours to prevent merge conflicts.
Format: `<type>/<ticket-id>-<short-description>`

**Permitted Types:**
*   `feat/`: A new mathematical model, API endpoint, or systemic feature. *(e.g., `feat/2.1-garch-volatility`)*
*   `fix/`: A patch for a bug or mathematically incorrect logic. *(e.g., `fix/1.5-hampel-nan-error`)*
*   `docs/`: Changes strictly to Markdown documentation. *(e.g., `docs/cloud-migration-update`)*
*   `refactor/`: Code changes that neither fix a bug nor add a feature (e.g., optimizing loop speed). *(e.g., `refactor/numba-array-loop`)*
*   `test/`: Adding or correcting `pytest` matrices.

### 4.2 Conventional Commits Standard
Commit messages act as the immutable ledger of our engineering intent. We strictly follow the [Conventional Commits V1.0](https://www.conventionalcommits.org/) specification.

**Format:**
```text
<type>(<scope>): <subject>

[optional body]
```

**Examples:**
*   ✅ `feat(ingestion): implement CCXT async websocket loop`
*   ✅ `fix(math): correct SQN division by zero error`
*   ✅ `docs(strategy): update Phase 9 cloud migration architecture`
*   ❌ `fixed the bug` (Violates protocol, will be rejected by CI)

### 4.3 Pull Request (PR) Template & Standards
Direct commits to the `main` branch are strongly prohibited. All code enters `main` exclusively via a Pull Request. Every PR description must follow this explicit template:

```markdown
**Ticket:** [Link to Ticket e.g., Ticket 2.1]
**Type:** [Feature | Bugfix | Refactor | Docs]

**1. Description of Changes**
[Explain exactly what structural changes were made to the codebase.]

**2. Mathematical / Logic Validation**
[Provide proof that the math works. e.g., "Ran pytest on statmodels ADF test, returning p-value < 0.05 on mock arrays."]

**3. Breaking Changes?**
[Yes/No. If yes, explain what database schemas or API contracts must be updated.]
```

### 4.4 Code Review & Merge Protocol
1.  **Branch Protection:** `main` requires at least 1 approving review (Human or AI Agent) before merging.
2.  **Continuous Integration (CI):** GitHub Actions will automatically run `flake8`, `black`, and quantitative `pytest` suites. If a PR fails the math tests, the "Merge" button statically locks.
3.  **Squash and Merge Only:** When a PR is approved, we execute a "Squash and Merge." This crushes multiple messy micro-commits from the feature branch into a single, clean, atomic Conventional Commit on `main`.

---

## Pillar 5: AI-Augmented Quantitative Engineering

We treat the AI (Antigravity/Claude) not as a subservient code-generator, but as a Lead Quantitative Architect. However, Large Language Models (LLMs) hallucinate if deprived of strict context parameters. We enforce the following AI collaboration protocols:

1.  **Contextual Anchor Injection:** Never ask the AI to "write a feature" blindly. You must forcefully anchor its context to the Master Strategy. *(Correct Prompt: "Read `docs/strategy/02_cointegration_arb.md` and implement the Johansen matrix in `math_core.py`.")*
2.  **The View-Before-Edit Mandate:** Ensure the AI invokes the `view_file` tool to read the current systemic state of the target file before running a codebase-altering `multi_replace`. Blind edits cause catastrophic indentation failures.
3.  **Strict Mode Separation (Planning vs Execution):** We explicitly separate AI execution boundaries. When the AI is in `PLANNING` mode, it is strictly forbidden from editing physical python files. Only once a technical `implementation_plan.md` artifact is approved by the human operator does the agent shift to `EXECUTION` mode to safely manipulate code.
4.  **Mathematical TDD Integration:** Before the AI writes the strategy function, mandate it to write the `pytest` mathematical proof array first. (e.g., "Write a pytest verifying the Hampel Filter returns a MAD of $X$ given array $Y$, then establish the core function.")

---

## Pillar 6: The Execution Runbook (Zero-to-One Provisioning)

With the theoretical foundations locked (Pillars 1-5), the Infrastructure Engineer executes this precise sequence to physically manifest the STOCKSTATS architecture. This guide takes a blank Ubuntu 24.04 LTS Basement Server (Bare-Metal strictly or a Dedicated Virtual Machine) and provisions it fully to host remote developers.

### 🗺️ Infrastructure Architecture (Basement Topology)

```mermaid
graph TD
    classDef prod fill:#ffebee,stroke:#f44336,stroke-width:2px;
    classDef dev fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    classDef vpn fill:transparent,stroke:#3498db,stroke-dasharray: 5 5;
    
    subgraph DevBox ["Linux Basement Server (Dedicated VM or Bare-Metal)"]
        
        subgraph DevNet ["Development Network"]
            TSDB_DEV[(TimescaleDB :5432)]:::dev
            REDIS_DEV[(Redis :6379)]:::dev
            PYTHON_DEV[VS Code Python Env<br/>Math & Shadow Engine]:::dev
        end
        
        subgraph ProdNet ["Production Docker Network (Isolated)"]
            TSDB_PROD[(TimescaleDB :5434)]:::prod
            PROD_APP[StockStats Prod Container<br/>Live Trading API Keys]:::prod
        end
        
        PYTHON_DEV -->|Reads| TSDB_DEV
        PROD_APP -->|Executes Binance| TSDB_PROD
    end
    
    subgraph Remote ["Remote Developer (MacBook)"]
        VS["VS Code Remote-SSH"]
    end
    
    VS -.->|Secure Tailscale VPN| PYTHON_DEV
```

### Step 1: The Cryptographic Network Layer (Tailscale & UFW)
Before any code touches the server, we must build the encrypted perimeter and lock the gates.

1.  **Install the Mesh VPN:** 
    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --ssh
    ```
    *Note the assigned 100.x.y.z IP address. This is now the ONLY way to reach the server.*
2.  **Lock the Firewall (UFW):**
    ```bash
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow in on tailscale0
    sudo ufw enable
    ```
3.  **Harden SSH Configurations (`/etc/ssh/sshd_config`):** Disable legacy vulnerabilities.
    ```text
    PasswordAuthentication no
    PermitRootLogin no
    PubkeyAuthentication yes
    ```
    *Execute `sudo systemctl restart ssh`.*

4.  **Validation:** 
    From the MacBook over external Wi-Fi (not Tailscale), attempt `ssh root@<public_ip>`. It **must** physically reject the connection. Attempt `ping 100.x.y.z`; it **must** return packets.

### Step 2: Linux Role-Based Access Control (RBAC)
We never operate as `root`. We provision isolated engineering profiles.

1.  **Create the Quant Developer Account:**
    ```bash
    sudo adduser dev_quant
    sudo usermod -aG sudo dev_quant
    sudo usermod -aG docker dev_quant  # Permits container execution without sudo
    ```
2.  **Inject the ED25519 Public Key:**
    From your MacBook, generate a modern key (`ssh-keygen -t ed25519`). Copy the `.pub` file contents.
    On the server:
    ```bash
    sudo su - dev_quant
    mkdir -p ~/.ssh && chmod 700 ~/.ssh
    nano ~/.ssh/authorized_keys # Paste public key here
    chmod 600 ~/.ssh/authorized_keys
    exit
    ```

3.  **Validation:**
    Close all connections. From the MacBook, execute `ssh dev_quant@100.x.y.z`. You must drop immediately into the server shell without being prompted for a password. Execute `docker ps`; it must succeed without throwing a permissions error.

### Step 3: Directory Scaffolding & Secrets Injection
The application architecture demands strict multi-directory separation.

1.  **Build the Physical Repository:**
    ```bash
    sudo mkdir -p /opt/stockstats/{backend,docs,frontend}
    sudo mkdir -p /opt/stockstats/backend/{core,ingestion,execution,database}
    sudo mkdir -p /opt/stockstats/docker-volumes/{timescaledb,redis}
    sudo chown -R dev_quant:dev_quant /opt/stockstats
    cd /opt/stockstats
    ```
2.  **Inject the 12-Factor `.env` Bindings:**
    ```bash
    nano .env
    ```
    ```env
    # Database Configuration (Timescale)
    POSTGRES_USER=stockstats_admin
    POSTGRES_PASSWORD=super_secure_dev_password_123!
    POSTGRES_DB=stockstats
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    
    # In-Memory Configuration (Redis)
    REDIS_HOST=localhost
    REDIS_PORT=6379
    
    # Execution Engine Protocol
    STOCKSTATS_EXECUTION_MODE=SHADOW
    ```
3.  **Sanitize the Git Commit Feed:**
    ```bash
    nano .gitignore
    ```
    ```text
    .env
    venv/
    __pycache__/
    docker-volumes/
    .DS_Store
    ```

4.  **Validation:**
    Execute `ls -la /opt/stockstats/`. Verify the `.env` file exists and that the owner is explicitly `dev_quant:dev_quant`. Git commit a test file and verify the `.env` is structurally ignored by examining `git status`.

### Step 4: Provisioning the Dockerized Storage Layer
We explicitly separate the databases into Linux containers with violent memory limitations to prevent OOM panics.

1.  **Construct the Orchestrator:**
    ```bash
    nano docker-compose.yml
    ```
    ```yaml
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
          - ./docker-volumes/timescaledb:/home/postgres/pgdata/data
        ports:
          - "5432:5432"
        deploy:
          resources:
            limits:
              memory: 16G # Critical guard against array queuing
        logging:
          driver: "json-file"
          options:
            max-size: "50m"
            max-file: "3"
        restart: unless-stopped
    
      redis:
        image: redis:7-alpine
        container_name: stockstats_redis
        command: redis-server --save 60 1 --loglevel warning
        volumes:
          - ./docker-volumes/redis:/data
        ports:
          - "6379:6379"
        deploy:
          resources:
            limits:
              memory: 4G # Bound cache to prevent OS starvation
        restart: unless-stopped
    ```
2.  **Ignite the Containers:**
    ```bash
    docker compose up -d
    docker ps  # Verify healthy ports 5432 and 6379
    ```

3.  **Validation:**
    The containers must be alive. We must verify the port bindings mathematically.
    *   Test TimescaleDB: `docker exec -it stockstats_timescaledb psql -U stockstats_admin -d stockstats -c "\dt"` (Should return relations or Empty).
    *   Test Redis: `docker exec -it stockstats_redis redis-cli ping` (Should physically return `PONG`).

### Step 5: The Python Quantitative Core
The system relies on LLVM compilers (`numba`). Version parity is legally binding.

1.  **Construct the Virtual Vacuum:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```
2.  **Lock the Dependencies (`requirements.txt`):**
    ```text
    ccxt[async]==4.2.35      # Async Exchange Websockets
    numpy==1.26.4            # Array manipulation (Must identically match Numba limits)
    pandas==2.2.1            # Time-series DataFrames
    numba==0.59.1            # LLVM Math Compiler for Hampel/GARCH
    asyncpg==0.29.0          # Async PostgreSQL Driver (Fast Inserts)
    redis==5.0.3             # Async Redis Pub/Sub
    python-dotenv==1.0.1     # Environment variable injection
    ```
3.  **Compile:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Validation:**
    We must verify the LLVM math compiler bound correctly to NumPy. Write a temporary test file.
    ```bash
    python3.11 -c "import numba; print(f'Numba injected successfully: {numba.__version__}')"
    ```
    (Must output `Numba injected successfully: 0.59.1` without throwing C-compiler errors).

### Step 6: The Remote Developer Verification (Final Application)
The infrastructure is ready. Now the human engineer remotely boots the VS Code GUI interface.

1.  **MacBook Setup:** Install the `Remote - SSH` extension authored by Microsoft in Visual Studio Code.
2.  **Configure the Local SSH Map (`~/.ssh/config`):**
    ```text
    Host StockStats-Basement
        HostName 100.x.y.z  # The Tailscale IP
        User dev_quant
        IdentityFile ~/.ssh/id_ed25519
    ```
3.  **Connect and Verify:**
    *   Click the green `><` icon in VS Code's bottom left.
    *   Select "Connect to Host" $\rightarrow$ `StockStats-Basement`.
    *   Once connected, select "Open Folder" $\rightarrow$ `/opt/stockstats/`.
    *   Open a new terminal inside VS Code. It will read `dev_quant@basement_server: /opt/stockstats$`. 

4.  **Validation:**
    Inside the VS Code terminal, execute `source venv/bin/activate` followed by `python --version`. It must state `Python 3.11.x`. Your IDE is now executing code directly on the Basement Server's CPU securely over the VPN.
    
**The Foundation is poured.** You are now physically ready to begin Sprint 2: Coding the Ingestion Engine.

---
**⬅️ Previous:** [Implementation Index](00_implementation_index.md) | **Next:** [Sprint 2: The Ingestion Gateway](02_sprint_2_ingestion_engine.md) ➡️
