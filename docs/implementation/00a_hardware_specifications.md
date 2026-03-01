# Prerequisite: Hardware & Infrastructure Sizing

## The Objective
As we transition from theory to execution, it is critical to understand that the physical machines running the STOCKSTATS codebase must scale alongside the software phases. Running a 50-asset high-frequency tick scrubber requires profoundly different hardware than training an XGBoost gradient tree.

This document defines the exact physical requirements for the machines operating each stage of the Minimum Viable Product (MVP) and beyond.

---

## 1. Sprints 1-5: The Phase 1 MVP (Centralized Basement Server)

During the first 5 Sprints, the goal is building the data pipeline, running the math, and executing trades manually via the Phase 3 Grafana UI. We are *not* competing with HFTs for 5-millisecond latency yet. We are prioritizing cost (free) and iteration speed. 

Instead of developers working in silos on thin-client laptops, we highly recommend utilizing a **Centralized Basement Server** (DevBox & Data Hub) from Day 1.

**Target Environment:** The Basement Server (e.g., High-End Desktop/Server hardware running Ubuntu Linux).

### The Architecture: How to use the server from Day 1
*   **Persistent Data Ingestion:** The server runs the `docker-compose.yml` (TimescaleDB & Redis) continuously 24/7. This guarantees an unbroken, massive historical dataset of L1 ticks. If developers run ingestion on their laptops, the data stream breaks every time they close the lid.
*   **Centralized Database Node:** Both local and remote developers connect to the *same* database over a secure VPN (e.g., Tailscale, WireGuard) or SSH tunnels. The entire team analyzes the same sterile ticks.
*   **VS Code Remote Development:** Developers do not run Python execution logic on their Macs. They use the **VS Code Remote - SSH extension** to physically write, debug, and execute the backend microservices directly on the basement server's compute cycles.
*   **Centralized Grafana:** The basement server hosts port `:3000`. Any operations staff member on the VPN simply navigates to `http://<basement-server-ip>:3000` to monitor the live trading command center.

### Minimum Hardware Specifications
*   **CPU:** 8+ Cores (e.g., Intel i7/i9, AMD Ryzen 7/9).
    *   *Why?* The server is simulating execution loops, scrubbing millions of ticks, compiling Numba matrices, and handling simultaneous remote SSH developer sessions.
*   **RAM:** 32 GB Minimum (64 GB Highly Recommended).
    *   *Why?* TimescaleDB requires 4-6 GB of RAM. Redis consumes ~2 GB. If 3 developers are simultaneously running data-heavy Pandas backtests on the server, memory consumption will spike dramatically.
*   **Storage:** 1 TB NVMe SSD.
    *   *Why?* TimescaleDB writes furiously 24/7. An NVMe drive is mandatory to prevent I/O queuing.
*   **Network:** Stable 500+ Mbps Fiber connection. The server needs high upload bandwidth to stream Grafana panels and VS Code Remote environments to your distributed developers.

---

## 2. Sprints 6-9: Phase 5 Autonomous Execution (Cloud VPC)

The moment we generate an API key with `Trade` permissions and launch the Sprint 7 CCXT Execution Router, the system **cannot** exist on a laptop. If the local ISP drops, or the MacBook goes to sleep, the `HTTP 504 Rescue Interrogator` (Sprint 9) dies, leaving "Zombie Orders" on the exchange.

**Target Environment:** Dedicated Virtual Private Server (VPS). Cloud Providers like AWS (EC2), Google Cloud, or DigitalOcean.

### Minimum Hardware Specifications
*   **Machine Type:** Compute-Optimized Droplet / EC2 Instance (e.g., AWS `c6i.xlarge` or DigitalOcean Premium Intel).
*   **CPU:** 4 vCPUs (Dedicated). Do *not* use "Shared CPU" instances. Noisy neighbors on a shared VPS will spontaneously spike our CPU latency, corrupting the microsecond micro-structure math.
*   **RAM:** 16 GB ECC RAM.
*   **Storage:** 200 GB NVMe Block Storage.

### The Geo-Location Mandate (Latency Arbitrage)
Where the VPS physically sits is the most important hardware decision in Phase 5.
*   **Binance Execution:** Binance servers are predominantly located in Tokyo (AWS `ap-northeast-1`). 
*   **The Mandate:** You must physically rent your VPS in Tokyo. Running the Execution Router from an AWS server in New York introduces $150$ milliseconds of physical fiber-optic latency. By co-locating the VPS in Tokyo, our TCP handshake with Binance drops to $< 5$ milliseconds, allowing us to dodge HFT spoofing.

---

## 3. Sprint 10: Phase 8 Machine Learning (GPU Acceleration)

Sprint 10 alters the hardware paradigm. Compiling fractional differenced features over millions of historical rows and training XGBoost gradient trees across 100 boosting rounds is catastrophically slow on a standard CPU.

**Target Environment:** Temporary GPU Cloud Instance (e.g., AWS EC2 `g4dn.xlarge` or RunPod).

### Minimum Hardware Specifications
*   **CPU:** 8+ vCPUs.
*   **RAM:** 32+ GB RAM (Loading massive Pandas `DataFrames` for historical simulation requires enormous memory).
*   **GPU (Critical):** 1x NVIDIA T4 (or stronger, e.g., A10G / V100).
    *   *Why?* XGBoost natively supports CUDA acceleration (`tree_method='hist'`, `device='cuda'`). A model training cycle that takes 45 minutes on an Apple M1 CPU will take $< 2$ minutes on a dedicated NVIDIA T4 GPU.
*   **Cost Strategy:** We **do not** leave this machine running 24/7. We spin up the GPU instance strictly to train the model, save the `meta_model.json` file, and instantly terminate the expensive proxy. The resulting JSON file is only $\approx 2$ MB and is copied back to our cheap Tokyo Execution VPS, where standard CPUs can execute *predictions* in sub-milliseconds.

---
**⬅️ Previous:** [Implementation Index](00_implementation_index.md) | **Next:** [Sprint 1: Core Infrastructure](01_sprint_1_infrastructure.md) ➡️
