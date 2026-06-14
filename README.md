# Cloud Native & DevOps Labs Workspace

Welcome to my central hands-on repository for Cloud Native technologies. This workspace is designed to document my practical journey through containerization, orchestration, and modern infrastructure automation using industry-standard tools like **Docker** and **Kubernetes**.

---

## 📂 Repository Roadmap & Index

This repository is strictly organized into logical modules. Each lab contains its own declarative configuration files (`.yaml` / `Dockerfile`) and a dedicated execution guide.

### ☸️ Kubernetes Labs (Orchestration)
| Lab ID | Topic / Focus | Core Components Used | Documentation |
| :--- | :--- | :--- | :--- |
| **Lab 01** | Multi-Node Cluster Topology & Service Routing | KinD, Namespaces, Pods, NodePort Service | [View Lab 01 Guide](./kubernetes/lab-01-kind-nginx/) |
| **Lab 02** | *Coming Soon (Deployments & ReplicaSets)* | -- | -- |

### 🐋 Docker Labs (Containerization)
| Lab ID | Topic / Focus | Core Components Used | Documentation |
| :--- | :--- | :--- | :--- |
| **Lab 01** | *Coming Soon (Dockerfile Basics & Image Building)* | -- | -- |
| **Lab 02** | *Coming Soon (Docker Volumes & Networking)* | -- | -- |

---

## 🛠️ Local Prerequisites Used Across Labs
To spin up and interact with the labs in this repository, the following tools are utilized on the host machine:
* **Docker Desktop** (Engine backend)
* **KinD (Kubernetes-in-Docker)** (Local cluster provisioning)
* **kubectl** (Kubernetes command-line interface)

---

## 📈 Goals of this Repository
1. **Infrastructure as Code (IaC):** Mastering declarative definitions over manual setups.
2. **Networking Deep Dives:** Understanding packet flow from the host browser to deeply isolated container networks.
3. **Production Best Practices:** Utilizing namespaces for resource isolation and native objects for lifecycle management.