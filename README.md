# 🚀 Cloud Native, DevOps & DevSecOps Labs Workspace

Welcome to my central hands-on repository for Cloud Native technologies. This workspace documents my practical journey through containerization, orchestration, and infrastructure automation using industry-standard tools like **Docker**, **Ansible**, and **Kubernetes**.

---

## 📂 Repository Roadmap & Index

This repository is strictly organized into logical modules. Each lab contains its own declarative configuration files (`.yaml`, `.ini`, `.yml`, or `Dockerfile`) alongside a dedicated execution guide.

### ☸️ Kubernetes Labs (Orchestration & Scaling)
| Lab ID | Topic / Focus | Core Components Used | Documentation |
| :--- | :--- | :--- | :--- |
| **Lab 01** | Multi-Node Cluster Topology & Service Routing | KinD, Namespaces, Pods, NodePort Service | [View Lab 01 Guide](./kubernetes/lab-01-kubernetes-kind-nodeport/) |
| **Lab 06** | Horizontal Pod Autoscaler (HPA) Traffic Management | Metrics Server, CPU Stress-Testing, Patches | [View Lab 06 Guide](./kubernetes/lab-6-k8s-autoscaling/) |
| **Lab 07** | Stateful Workloads & Persistent Storage | StatefulSet, Headless Services, PVC | [View Lab 07 Guide](./kubernetes/lab-7-statefulset-lab/) |

### 🐋 Docker & Automation Labs (Containerization & DevSecOps)
| Lab ID | Topic / Focus | Core Components Used | Documentation |
| :--- | :--- | :--- | :--- |
| **Lab 00** | Automated Multi-Node Pipeline & Network Hardening | Ansible, Docker-in-Docker, Flask, PostgreSQL | [View Lab 00 Guide](./docker/lab-00-mini-project-docker-ansible/) |

---

## 🏗️ Highlighted Architectures

### 1. Multi-Node Automation Pipeline (`Docker/Lab-00`)
Simulates a real-world production environment inside an isolated control network. Ansible orchestrates a dedicated App Node (Flask REST API) and Storage Node (PostgreSQL & pgAdmin) with cryptographic RSA authentication and hardened secrets management.

### 2. Network Traffic Routing (`Kubernetes/Lab-01`)
Demonstrates how incoming external host machine traffic maps natively into a deeply isolated cluster network using synchronized ports:
```text
[Local Browser: Port 8000] ──> [KinD Virtual Worker Node: Port 30002] ──> [Nginx Pod: Port 80]

```

### 3. Automated Demand Elasticity (`Kubernetes/Lab-06`)

Deploys an automated scaling loop using a local Metrics Server bypass patch. When simulated stress traffic spikes the cluster CPU, the HPA controller duplicates pods from 1 to 5 replicas dynamically, downscaling gracefully once demand drops.

---

## 🛠️ Local Prerequisites Used Across Labs

To spin up and interact with the labs in this repository, the following tools are utilized on the host machine:

* **Docker Desktop** (Engine backend & containerization transport)
* **Ansible** (Configuration management and pipeline transport)
* **KinD (Kubernetes-in-Docker)** (Local multi-node cluster provisioning)
* **kubectl** (Kubernetes CLI management plane)

---

## 📈 Goals of this Repository

1. **Infrastructure as Code (IaC):** Mastering declarative lifecycle definitions over manual setups.
2. **Advanced Network Engineering:** Understanding precise packet flow from the host operating system browser to isolated target container subnets.
3. **Enterprise Security Practices:** Implementing strict environment separation via Namespaces, local TLS bypass patching, and robust credential hashing.

---

## 📬 Contact & Support

If you have any questions, run into issues setting up the labs, or want to chat about cloud-native architecture, feel free to reach out:

* **Email:** [eliyahoob@gmail.com](mailto:eliyahoob@gmail.com)

