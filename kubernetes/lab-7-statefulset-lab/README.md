# Kubernetes StatefulSet Architecture & Lifecycle Lab

This lab demonstrates how a Kubernetes `StatefulSet` manages stateful applications by providing **stable network identities** and **persistent, dedicated storage**. Unlike standard Deployments, StatefulSets ensure that Pod identity and data persist across restarts, scaling, and updates.

---

## Core Concepts: Why use a StatefulSet?

Standard Deployments are for *stateless* apps (like web frontends), where Pods are identical and interchangeable. A `StatefulSet` is required for *stateful* applications (databases, queues) that need:

* **Stable Network Identity:** Pods retain fixed names (`web-0`, `web-1`) instead of random hashes.
* **Persistent Storage Binding:** Each individual Pod is permanently mapped to its own unique storage disk (Persistent Volume).
* **Ordered Execution:** Pods are created, scaled, or destroyed sequentially (one by one), never all at once.

**Common Use Cases:** MySQL, PostgreSQL, MongoDB, Apache Kafka, and Elasticsearch.

---

## Pre-Lab: Environment Cleanup

Before starting, ensure your cluster is completely clear of older lab resources to avoid naming conflicts.

```powershell
# 1. Check what is currently running
kubectl get all

# 2. Force delete any remaining Persistent Volume Claims (Critical for StatefulSets)
kubectl delete pvc --all

# 3. Clean up all other running resources
kubectl delete all --all

```

---

## Guided Lab Steps (01 - 09)

#### Step 01: Deploy the Headless Service

A Headless Service (`clusterIP: None`) is responsible for discovering and establishing the stable network routing directly to your individual stateful Pods.

```powershell
# Apply the service manifest
kubectl create -f service.yaml

# Verify the service is created and check that CLUSTER-IP is 'None'
kubectl get svc nginx

```

#### Step 02: Deploy the StatefulSet configuration

This manifest defines our stateful application layout, spinning up Nginx pods alongside a template to dynamically provision private storage for each replica.

```powershell
# Apply the statefulset manifest
kubectl create -f statefulset.yaml

# Verify deployment registration
kubectl get statefulsets web

```

#### Step 03: Prove Stable & Ordered Initialization

**Goal:** Observe that Kubernetes initializes Pods sequentially by index (0, then 1, then 2) rather than creating them simultaneously.

```powershell
# Watch the pods spawn live
kubectl get pods -l="app=nginx" --watch

```

* **The Proof:** You will see `web-0` transition to `Running` and `Ready` **before** `web-1` begins creating. They will always preserve these exact index names.

#### Step 04: Prove Persistent Volume Relationships (Windows Adjusted)

**Goal:** Verify that every unique Pod has a corresponding logical claim (PVC) bound to a dedicated physical disk (PV).

```powershell
# View physical storage availability
kubectl get pv

# View logical claims and notice how the Pod index matches the disk index
kubectl get pvc | ForEach-Object { $fields = $_ -split '\s+'; if ($fields[0]) { "$($fields[0]) -------> $($fields[2])" } }

```

* **The Proof:** Your output will show a direct pairing mapping specific Pod attachments:
* `www-web-0` is bound uniquely to its own `pvc-xxxx...`
* `www-web-1` is bound uniquely to its own `pvc-yyyy...`



#### Step 05: Prove Ordered Scaling Up

**Goal:** Increase application footprint from 3 replicas to 5 and observe controlled, predictable expansion.

```powershell
# 1. Edit the manifest live: Change 'replicas: 3' to 'replicas: 5'
kubectl edit statefulset web

# 2. Instantly watch the sequential expansion
kubectl get pods -l="app=nginx" --watch

```

* **The Proof:** Pods `web-3` and `web-4` are appended safely to the chain one after another without altering the identity or state of `web-0` through `web-2`.

#### Step 06: Prove Data Protection & Ordered Scaling Down

**Goal:** Scale down from 5 replicas down to 2 and verify how Kubernetes handles storage removal safety.

```powershell
# 1. Edit the manifest live: Change 'replicas: 5' to 'replicas: 2'
kubectl edit statefulset web

# 2. Watch the termination sequence
kubectl get pods -l="app=nginx" --watch

```

* **The Proof (Order):** Pods are deleted in strict reverse order (`web-4` terminates completely first, then `web-3`).
* **The Proof (Data Safety):** Run `kubectl get pvc`. Notice that even though the Pods are gone, their underlying disks (`www-web-3`, `www-web-4`) **remain intact** so your application data is never accidentally lost during down-scaling!

#### Step 07: Trigger a Rolling Update

**Goal:** Upgrade the underlying application image safely across your stateful infrastructure.

```powershell
# Edit the manifest live: Locate 'image: gcrcontainer/nginx-slim:0.20'
# and update it to 'image: gcrcontainer/nginx-slim:0.26'
kubectl edit statefulset web

```

#### Step 08: Prove Rolling Update Safety

**Goal:** Confirm the cluster upgrades pods systematically to prevent application downtime.

```powershell
# 1. Monitor rolling progress status
kubectl rollout status statefulset web

# 2. Verify image tag version on active Pods (PowerShell Alternative)
kubectl describe pod web-0 | Select-String "Image:"

```

* **The Proof:** Kubernetes updates the Pods one by one. It safely updates `web-1`, brings it back to operational readiness, and only then proceeds to update `web-0`, maintaining overall cluster availability throughout the process.

#### Step 09: Prove Rollback Capabilities

**Goal:** Safely revert your stateful cluster back to its previous software version if bugs are detected.

```powershell
# 1. Undo the previous update command
kubectl rollout undo statefulset web

# 2. Await rollback validation
kubectl rollout status statefulset web

# 3. Double-check image specs to verify version degradation
kubectl describe pod web-0 | Select-String "Image:"

```

* **The Proof:** The image definition will safely return to `gcrcontainer/nginx-slim:0.20` without corrupting your persistent disk storage bindings.