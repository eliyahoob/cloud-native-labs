# Practical Guide: Managing Kubernetes StatefulSets (Lab 7)

This guide walks you through Lab 7 and is tailored for **Windows PowerShell**. It provides concise explanations, Windows-compatible commands, and a clear look into StatefulSet storage and identity architecture.

---

## 1. Core Concepts

Unlike a standard Deployment that manages stateless applications, a **StatefulSet** is designed for applications that require a persistent state, such as databases (MySQL, PostgreSQL, MongoDB, Kafka).

It guarantees:

* **Stable Network Identity:** Pod names are persistent and do not change across restarts.
* **Persistent Storage:** Each Pod is mapped to its own dedicated, permanent disk.
* **Ordered Operations:** Pod startup, shutdown, and scaling occur sequentially rather than simultaneously.

### Storage Architecture: PV vs. PVC

* **PV (Persistent Volume):** The actual physical disk resource provisioned in the cluster (e.g., cloud storage, network share, or local disk).
* **PVC (Persistent Volume Claim):** The logical request made by the application/Pod to consume storage. The PVC links the Pod to the physical PV.

---

## 2. Environment Cleanup

Before starting, ensure your environment is clean of old resources to prevent conflicts.

```powershell
# List all existing resources
kubectl get all

# Delete all existing PVCs in the cluster
kubectl delete pvc --all

# Delete other existing resources (Deployments, Services, Pods)
kubectl delete all --all

# Verify the environment is completely clear
kubectl get all

```

---

## 3. Step-by-Step Lab Walkthrough (PowerShell)

### Step 01: Create a Headless Service

The Service assigns a stable network identity to the StatefulSet Pods. Setting `clusterIP: None` (Headless) allows direct routing to the individual Pod IP addresses.

```powershell
# Create the service from the file
kubectl create -f service.yaml

# Verify the service exists
kubectl get svc

```

### Step 02: Create the StatefulSet

Now, we deploy the StatefulSet which initializes 3 Nginx Pods, each requesting 1Gi of storage.

```powershell
# Create the StatefulSet
kubectl create -f statefulset.yaml

# Verify the StatefulSet status
kubectl get statefulsets

```

### Step 03: Inspect the Pods (Stable Identity)

Notice that the Pods are created sequentially (`web-0`, then `web-1`, then `web-2`) rather than all at once.

```powershell
# Filter and list Pods belonging to the application
kubectl get pods -l="app=nginx"

```

*Expected Output:* Fixed ordinal names: `web-0`, `web-1`, `web-2`.

### Step 04: Inspect Storage (PV and PVC)

Since Linux string utilities (`awk`) do not work in standard PowerShell, use these native commands to inspect your storage layer:

```powershell
# List the physical Persistent Volumes (PV)
kubectl get pv

# List the logical Persistent Volume Claims (PVC)
kubectl get pvc

```

*Key takeaway:* Each Pod (e.g., `web-0`) gets a dedicated PVC named `www-web-0` bound to a specific PV.

### Step 05: Scale Up the StatefulSet

We will increase the number of replicas from 3 to 5.

```powershell
# Open the live configuration editor. 
# Find the line 'replicas: 3' and change it to 'replicas: 5'
kubectl edit statefulset web

# Monitor the sequential creation of the new Pods (Press Ctrl+C to exit)
kubectl get pods -l="app=nginx" --watch

```

*StatefulSet Behavior:* `web-3` will be fully created and running before `web-4` begins initializing.

### Step 06: Scale Down the StatefulSet

We will reduce the replicas from 5 back to 2.

```powershell
# Edit the configuration and change 'replicas: 5' to 'replicas: 2'
kubectl edit statefulset web

# Monitor the sequential termination of the Pods
kubectl get pods -l="app=nginx" --watch

```

*StatefulSet Behavior:* Termination occurs in reverse order (`web-4` is deleted first, followed by `web-3`). The physical storage disks (PVCs/PVs) **are not auto-deleted** during a scale-down to protect your data.

### Step 07: Perform a Rolling Update

Update the container image version from `0.20` to `0.26`.

```powershell
# Edit the StatefulSet configuration. Locate the 'image' field and change 
# gcrcontainer/nginx-slim:0.20 to gcrcontainer/nginx-slim:0.26
kubectl edit statefulset web

```

### Step 08: Watch Rollout Status & Verify

Updates are applied safely, one Pod at a time, in reverse ordinal order.

```powershell
# Monitor the deployment rollout progress
kubectl rollout status statefulset web

# Verify the image version using PowerShell's native 'Select-String' alternative to grep
kubectl describe pod web-0 | Select-String "Image:"
kubectl describe pod web-1 | Select-String "Image:"

```

### Step 09: Rollback the Update

If an issue occurs with the new image, you can instantly revert to the previous stable state.

```powershell
# Undo the last deployment and roll back to version 0.20
kubectl rollout undo statefulset web

# Track the rollback progress
kubectl rollout status statefulset web

# Confirm the Pods are back to version 0.20
kubectl describe pod web-0 | Select-String "Image:"

```

---

## 4. Troubleshooting Tips

* **CommandNotFoundException (`grep` / `awk`):** Always replace Linux pipes with native PowerShell tools. Use `Select-String` instead of `grep`. For complex output filtering, utilize Kubernetes native parameters like `-o jsonpath`.
* **Pods Stuck in `Pending` Status:** If your new pods cannot start, check if your cluster has available physical PVs matching the criteria requested in the `volumeClaimTemplates` block (e.g., 1Gi size or correct StorageClass). Run `kubectl describe pod <pod-name>` to view specific scheduling errors.