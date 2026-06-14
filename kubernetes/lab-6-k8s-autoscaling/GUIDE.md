# Kubernetes Horizontal Pod Autoscaler (HPA) - Beginner Guide

This guide explains how to make Kubernetes automatically add more application instances (Pods) when there is high traffic, and remove them when the traffic drops to save money.

---

## Step 1: Clean Up & Deploy the App
### We start by cleaning up any previous work and launching our web application (`php-apache`).

1. Open **PowerShell** in your lab folder.
2. Clear any old running resources:
   ```bash
   kubectl delete all --all
   ```
Run the web server using your YAML configuration file:

```Bash
kubectl apply -f autoscaling-hpa.yaml
```
Verify the application is running:

```Bash
kubectl get pods
```
You should see a pod named php-apache-xxx with the status Running.

## Step 2: Enable the Autoscaler (HPA)
### We set a rule telling Kubernetes when to scale our application.

Create a rule: If the CPU usage goes above 10%, automatically duplicate the pods (Minimum: 1 pod, Maximum: 5 pods):

```Bash
kubectl autoscale deployment php-apache --cpu-percent=10 --min=1 --max=5
```
Check the autoscaler status:

```Bash
kubectl get hpa
```
Note: Under the TARGETS column, you will see cpu: <unknown>/10%. This is because Kubernetes does not have a "sensor" installed yet to measure CPU usage.

## Step 3: Install the Sensor (Metrics Server)
### To fix the <unknown> error, we install the official tool that measures resource usage.

Download and install the Metrics Server:

```Bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```


## Step 4: Fix Security for Local Testing (Patch)
### Because we are running locally on Docker/Kind (and not on a secure cloud provider), the Metrics Server will fail due to strict SSL/TLS security checks. We need to tell it to bypass these checks locally.

Apply the security bypass patch (PowerShell optimized):

```Bash
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/args/-\",\"value\":\"--kubelet-insecure-tls\"}]'
```
Restart the Metrics Server to load the new setting:

```Bash
kubectl rollout restart deployment metrics-server -n kube-system
```
Wait 15 seconds, then check the status again:

```Bash
kubectl get hpa
```
The <unknown> error is gone! You will now see cpu: 2%/10% (or similar). The sensor is working.

## Step 5: Test the Stress Load
### Now we will flood the server with traffic to see the autoscaler in action.

In your current terminal, start watching the autoscaler live:

```Bash
kubectl get hpa --watch
```
Open a second (new) PowerShell window and create a temporary traffic generator pod:

```Bash
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- sh
```
Inside the new terminal prompt (/#), paste this loop to flood the server with requests and hit Enter:

```Bash
while sleep 0.01; do wget -q -O- http://php-apache; done
```

## Step 6: Observe the Magic
### Scale Up: 
Look back at your first terminal (--watch). Within 1–2 minutes, the CPU will spike (e.g., 110%/10%), and the REPLICAS count will automatically jump from 1 to 5 to handle the heavy load.

### Scale Down: 
Go to your second terminal (the one printing OK!) and press Ctrl + C to stop the traffic. Wait about 5 minutes. As the CPU drops back to 0%, Kubernetes will automatically delete the extra pods and scale back down to 1 replica to save resources.