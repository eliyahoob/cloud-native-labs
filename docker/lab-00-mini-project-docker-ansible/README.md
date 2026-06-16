# 🌐 Automated Multi-Node Infrastructure Pipelines (Ansible & Docker)

An enterprise-grade, automated DevSecOps infrastructure deployment. This project demonstrates how to orchestrate a distributed multi-node environment using **Ansible** as the automation engine and **Docker** for complete containerization and environmental isolation.

---

## 🏗️ System Architecture & Data Flow

The project simulates a full production data center locally using a **Docker-in-Docker (DinD)** approach to separate control networks from application runtimes.

```text
                     [ Developer PC / Host Machine ]
                                    │
                       (docker compose up -d)
                                    │
                                    ▼
                     [ Isolated Bridge Network ]
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
┌─────────────────┐                                  ┌─────────────────┐
│ ansible-slave-1 │                                  │ ansible-slave-2 │
│  (App Server)   │                                  │  (DB Server)    │
└────────┬────────┘                                  └────────┬────────┘
         │                                                    │
(Ansible Orchestration)                             (Ansible Orchestration)
         │                                                    │
         ▼                                                    ▼
   ┌───────────┐                                        ┌───────────┐
   │  web-app  │◄────────────[ REST API Link ]──────────┤ postgres  │
   │  (Flask)  │                                        │  pgadmin  │
   └───────────┘                                        └───────────┘

```

1. **The Control Plane (`ansible-master`)**: Establishes secure, passwordless SSH communication with target nodes using an RSA key-pair.
2. **The App Node (`ansible-slave-1`)**: Hosts the stateless Python Flask REST API backend.
3. **The Storage Node (`ansible-slave-2`)**: Houses the PostgreSQL database core alongside the pgAdmin management dashboard.

---

## ⚡ Quick Start (TL;DR)

For the full step-by-step documentation, security configurations, and troubleshooting, please refer to the detailed **[GUIDE.md](https://www.google.com/search?q=./GUIDE.md)**.

### 1. Provision the Lab Simulation Cluster

Navigate to the root configuration folder and spin up the multi-node infrastructure:

```bash
cd ansible
docker compose up -d

```

### 2. Trigger the Automation Pipeline

Enter the master controller node and execute the automated orchestration playbook:

```bash
# Exec into the master controller
docker exec -it ansible-master bash

# Run the deployment
cd /lab-00-mini-project-docker-ansible/ansible
ansible-playbook -i inventory.ini deploy.yml

```

### 3. Verify Live Endpoints

* **Flask REST API:** `http://localhost:5000/users`
* **pgAdmin Panel:** `http://localhost:8080`

---

## 🧹 Quick Cleanup

To gracefully stop all components and wipe custom networks/persistent data:

```powershell
cd ansible && docker compose down && cd ../app && docker compose down && cd ../database && docker compose down

```

## 🛠️ Tech Stack & Core Tools

* **Orchestration:** Ansible (Targeting Ubuntu 22.04 LTS environments)
* **Containerization:** Docker Engine & Docker Compose (v3.8)
* **Backend:** Python 3.11-slim / Flask Framework
* **Database:** PostgreSQL 15-alpine & pgAdmin 4

## 📬 Contact & Support
If you have any questions, run into issues setting up the lab, or want to chat about the architecture, feel free to reach out:

* **Email:** [eliyahoob@gmail.com](mailto:eliyahoob@gmail.com)