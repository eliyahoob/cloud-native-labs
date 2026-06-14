# Kubernetes HPA (Horizontal Pod Autoscaler) Lab

A hands-on laboratory project demonstrating automated scaling in Kubernetes using the Horizontal Pod Autoscaler (HPA) and Metrics Server in a local development environment (Docker/Kind).

## 🚀 Project Overview
This project simulates real-world production traffic management. When a containerized PHP-Apache web server experiences a CPU spike due to high traffic, Kubernetes automatically scales the infrastructure from 1 to 5 replicas to balance the load, and safely shrinks back when traffic drops.

## 📂 Repository Structure
* `autoscaling-hpa.yaml` - The core deployment and service configuration file.
* `GUIDE.md` - Step-by-step documentation for beginners (includes screenshots/commands).
* `README.md` - Project overview and quick start guide (this file).

## 🛠️ Prerequisites
* Docker Desktop
* Kubernetes Cluster (Kind or Minikube)
* `kubectl` CLI installed

## ⚡ Quick Start (TL;DR)

If you already know the basics, run these commands in order using **PowerShell**:

```bash
# 1. Deploy the application
kubectl apply -f autoscaling-hpa.yaml

# 2. Setup HPA rule (Scale between 1-5 pods at 10% CPU target)
kubectl autoscale deployment php-apache --cpu-percent=10 --min=1 --max=5

# 3. Install Metrics Server
kubectl apply -f [https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml](https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml)

# 4. Patch Metrics Server for local TLS bypass
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# 5. Restart Metrics Server to apply changes
kubectl rollout restart deployment metrics-server -n kube-system