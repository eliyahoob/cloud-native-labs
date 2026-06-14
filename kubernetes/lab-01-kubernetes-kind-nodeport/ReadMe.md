# Local Kubernetes Deployment with KinD & NodePort Service

A hands-on DevOps project demonstrating how to architect and deploy a local Kubernetes infrastructure using **KinD (Kubernetes-in-Docker)**. This project showcases environment isolation via custom **Namespaces**, declarative application deployment with an **Nginx Pod**, and external traffic routing using a **NodePort Service**.

## Key Project Features
* **Multi-Node Infrastructure:** Programmatically provisions a cluster consisting of 1 Control-Plane and 1 Worker node.
* **Network Traffic Forwarding:** Implements an end-to-end routing pipeline mapping a local machine port directly into an isolated container cluster network without temporary port-forwarding commands.
* **Logical Resource Isolation:** Utilizes a dedicated Kubernetes Namespace to securely isolate development workloads.

---

## Network Architecture (How Traffic Flows)

Although the Nginx web server runs internally on an isolated cluster network (**Port 80**), it is exposed persistently to the host machine's browser via **Port 8000** (`http://localhost:8000`).

The infrastructure handles routing through 3 synchronized stations:

[Local Browser: Port 8000] ──> [KinD Node: Port 30002] ──> [Nginx Pod: Port 80]

1. **Station 1 (Host to Node):** Docker maps incoming traffic from the host machine on **Port 8000** (`hostPort`) directly to **Port 30002** (`containerPort`) on the cluster's virtual Worker Node.
2. **Station 2 (Entering the Cluster):** A Kubernetes **NodePort Service** binds to **Port 30002** across the nodes. It intercepts the incoming traffic and uses a `selector` label filter to match target Pods (`app: my-app`).
3. **Station 3 (Service to Pod):** The Service delivers the traffic directly into the backend application container running on **Port 80** (`targetPort`).

---

## Project Structure

* `kind-config.yaml` - KinD multi-node cluster topology definition.
* `ns-my-first-pod.yaml` - Declarative Namespace schema for resource isolation.
* `my-first-pod.yaml` - Pod deployment blueprint hosting the Nginx image.
* `my-first-service.yaml` - NodePort Service networking configuration.
* `Guide.md` - Step-by-step implementation logs and terminal outputs.

---

## Quick Start

To replicate this environment locally, ensure you have **Docker**, **KinD**, and **kubectl** installed, then execute:

```powershell
# 1. Provision the infrastructure
kind create cluster --name kind-01 --config kind-config.yaml

# 2. Deploy the network isolation layer
kubectl apply -f ns-my-first-pod.yaml
kubectl config set-context --current --namespace=test

# 3. Spin up the application and networking service
kubectl apply -f my-first-pod.yaml
kubectl apply -f my-first-service.yaml

