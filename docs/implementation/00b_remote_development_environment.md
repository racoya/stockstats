# Prerequisite: Centralized Remote Development Environment

## The Objective
As established in the [Hardware Sizing Matrix](00a_hardware_specifications.md), the STOCKSTATS Phase 1 MVP is powered by a Centralized Basement Server acting as a unified Data Hub and Compute Node.

This document provides the exact, copy-pasteable terminal commands required to configure this Ubuntu Linux server so that a team of 3+ developers and traders can securely log in, analyze the identical dataset, and cooperatively build the Python microservices without encountering the "it works on my machine" anti-pattern.

---

## Step 1: Operating System & Secure Networking

We do not expose the Basement Server directly to the public internet (no Port Forwarding on the router). We overlay a zero-config peer-to-peer VPN to create a secure, encrypted intranet.

**1.1 The Operating System:**
Install **Ubuntu Server 22.04 LTS** (or newer) on the Basement Server. During installation, ensure you select the option to install the `OpenSSH Server`.

**1.2 The Tailscale VPN Tunnel:**
Tailscale (built on Wireguard) allows remote developers in different cities to seamlessly SSH into the Basement Server as if they were sitting in the same room.

1.  Create a free [Tailscale admin account](https://tailscale.com/).
2.  SSH into your Basement Server locally (or run this physically on the machine):
    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up
    ```
3.  Authenticate the server. It will be assigned a static VPN IP address (e.g., `100.115.x.x`).
4.  Have all 3 Remote Developers download Tailscale for Mac/Windows and log into the same network.

## Step 2: Developer Access & SSH Keys

We strictly prohibit developers from logging in as `root`. Every developer gets an isolated Linux user account, allowing us to track git commits and file modifications perfectly.

**2.1 Provisioning the User Accounts:**
The Server Admin runs these commands on the Basement Server for each developer:

```bash
# Create the developer's Linux profile
sudo adduser dev_alice
sudo adduser dev_bob

# Add them to the 'sudo' group so they can install packages if necessary
sudo usermod -aG sudo dev_alice
sudo usermod -aG sudo dev_bob
```

**2.2 SSH Public Key Authentication:**
The developers must generate cryptographic SSH keys on their MacBooks. They send the Server Admin their **Public Key** (`id_rsa.pub` or `id_ed25519.pub`).

The Admin authorizes the key on the Basement Server:
```bash
# Switch to Alice's profile
su - dev_alice
mkdir ~/.ssh
chmod 700 ~/.ssh

# Paste Alice's public key into the authorized list
nano ~/.ssh/authorized_keys
# (Paste Key, Save, Exit)

chmod 600 ~/.ssh/authorized_keys
exit
```

## Step 3: Docker & Permissions

In Sprint 1, we will launch TimescaleDB and Redis via `docker-compose`. The developers need permission to start, stop, and inspect these containers without typing `sudo` every time.

**3.1 Install Docker Engine:**
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**3.2 The `docker` User Group:**
Add all developers to the Docker permission group.
```bash
sudo usermod -aG docker dev_alice
sudo usermod -aG docker dev_bob
# Note: Developers must log out and log back in for this group change to take effect.
```

## Step 4: The Shared Environment Hierarchy

To collaborate effectively, the repository must sit in a shared directory that all developers have full Read/Write access to, such as `/opt/stockstats/`.

**4.1 Configure the Shared Repository Space:**
```bash
# Create the shared directory
sudo mkdir -p /opt/stockstats
sudo chown -R root:sudo /opt/stockstats
sudo chmod -R 775 /opt/stockstats

# Alice clones the repo into the shared space
su - dev_alice
cd /opt
git clone <your-private-git-url> stockstats
```

## Step 5: VS Code Remote-SSH (The Developer Experience)

Developers **do not** write code in terminal `vim`. They write code locally on their pristine MacBooks, but the execution happens on the Basement Server.

**5.1 Developer Configuration (Run on the Developer's MacBook):**
1.  Open Visual Studio Code.
2.  Install the official Microsoft extension: **Remote - SSH**.
3.  Press `Cmd + Shift + P` -> **Remote-SSH: Open SSH Configuration File**.
4.  Add the Basement Server to the config:

```text
# ~/.ssh/config (On Developer's Mac)
Host StockStats-Basement
    HostName 100.115.x.x  # The Tailscale IP from Step 1
    User dev_alice        # Their specific Linux username
    IdentityFile ~/.ssh/id_ed25519 # The path to their private key
```

**5.2 Connecting and Compiling:**
1.  In VS Code, press `Cmd + Shift + P` -> **Remote-SSH: Connect to Host** -> Select `StockStats-Basement`.
2.  VS Code will instantly spawn a headless sub-server on the Ubuntu machine. The entire VS Code UI transforms to operate physically inside the Basement Server.
3.  Click **Open Folder** and select `/opt/stockstats/`.
4.  Open the integrated terminal (which is now a Basement Server bash shell).

Every line of Python Alice types is saved directly to the `/opt/stockstats/` structure on the server. When she types `python3 calculate.py`, it executes on the Server's 8-Core CPU, instantly querying the localhost TimescaleDB container without any network latency. 

## Step 6: Operation Staff (Grafana UI)

When Phase 3 (Manual Trading) activates, the non-developer Traders need to see the charts to make execution decisions.

They do not need SSH terminal access.
1.  The Trader connects their laptop to the Tailscale VPN.
2.  They open Chrome/Safari.
3.  They navigate to `http://100.115.x.x:3000` (The Grafana port mapped from Docker).
4.  The dashboards load seamlessly over the secure Intranet.

---
**⬅️ Previous:** [Hardware Sizing Matrix](00a_hardware_specifications.md) | **Next:** [Antigravity AI Integration](00c_antigravity_ai_integration.md) ➡️
