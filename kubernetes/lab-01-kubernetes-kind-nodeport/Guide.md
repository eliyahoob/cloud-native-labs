# Starting Nginx in local Kubernetes environment

<div style="background-color: #f0f4f8; padding: 15px; border-left: 4px solid #0066cc; border-radius: 4px;">
📂 <b>Project folder:</b><br>
All files we will create will be in the project directory.
All commands we will run from PowerShell in the project folder (even though some of them can run in other locations as well)
</div>

## Step 1: Create the cluster (infrastructure) using kind 

kind - https://kind.sigs.k8s.io/ (KinD -  Kubernetes In Docker)

We will use a tool called kind to turn our local PC to a cluster - meaning a system that knows
to manage and run Kubernetes containers on top of the Docker engine running on my PC.

### kind-config.yaml 

In our working directory we will create a simple yaml file 'kind-config.yaml' with the settings for the cluster:

```yaml
# Telling 'KinD' what type of object we will be creating. In this case, a cubernetes cluster.
kind: Cluster
# API version of KinD we will be using to read this file.
apiVersion: kind.x-k8s.io/v1alpha4
# List of "virtual servers" (Nodes) we will be creating in this cluster.
nodes:
# First "server": The control/management "server" of the cluster "the brain".
- role: control-plane
  # Routeing port 30000 on my PC to port 30000 in the control "server".
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
    listenAddress: "0.0.0.0" # Allowing access from any IP address
# Seconds server: The "Work Server" - here our apps and Pods will actually run.
- role: worker
  extraPortMappings:
  # Worker-First-Route: Routeing port 3000 in my PC, will route to port 30001 (!) in the worker server.
  - containerPort: 30001
    hostPort: 3000
    listenAddress: "0.0.0.0"
  # Worker-Second-Route: Port 8000 in your PC will route to port 30002
  - containerPort: 30002
    hostPort: 8000
    listenAddress: "0.0.0.0"
```

### Creating the cluster with the 'kind create cluster' command:
We will run the 'kind create cluster' command to create a cluster on my PC:

```powershell
kind create cluster --name kind-01 --config kind-config.yaml
```

A success run will look like this:
```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kind create cluster --name kind-01 --config kind-config.yaml
Creating cluster "kind-01" ...
 • Ensuring node image (kindest/node:v1.36.1) 🖼  ...
 ✓ Ensuring node image (kindest/node:v1.36.1) 🖼
 • Preparing nodes 📦 📦   ...
 ✓ Preparing nodes 📦 📦
 • Writing configuration 📜  ...
 ✓ Writing configuration 📜
 • Starting control-plane 🕹️  ...
 ✓ Starting control-plane 🕹️
 • Installing CNI 🔌  ...
 ✓ Installing CNI 🔌
 • Installing StorageClass 💾  ...
 ✓ Installing StorageClass 💾
 • Joining worker nodes 🚜  ...
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-kind-01"
You can now use your cluster with:

kubectl cluster-info --context kind-kind-01

Thanks for using kind! 😊
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```
You can see that the cluster is up and running and both "virtual servers" are connected to it:
```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS         PORTS                                                 NAMES
4dd329430162   kindest/node:v1.36.1   "/usr/local/bin/entr…"   4 minutes ago   Up 4 minutes   0.0.0.0:3000->30001/tcp, 0.0.0.0:8000->30002/tcp      kind-01-worker
43ea2fd16b25   kindest/node:v1.36.1   "/usr/local/bin/entr…"   4 minutes ago   Up 4 minutes   0.0.0.0:30000->30000/tcp, 127.0.0.1:62896->6443/tcp   kind-01-control-plane
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```

## Step 2: Creating a Namespace (a separated work envionment)

### ns-my-first-pod.yaml

We will create a yaml file for the name space configurations

```yaml
# V1 is a stable version for creating the Kubernetes object.
apiVersion: v1
# Setting the object we want to create using kind. In this case - Namespace.
kind: Namespace
# Metadata - general information about the object we're creating
metadata:
  # The unique name we will give this Namespace inside this cluster
  name: test
```

### Creating the cluster running the 'kubectl apply' command:

```powershell
kubectl apply -f ns-my-first-pod.yaml
```
A successfull run will look like:

```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kubectl apply -f ns-my-first-pod.yaml
namespace/test created
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>```


## Step 3: Setting the name space as 'default namespace':

To avoide the need to allways add the namespace (--namespace=test) to each command we later run, we will set 'test' as our default Namespace.
This will tell 'kubectl' that all our following commands are automatically belong to the 'test' Namespace

```powershell
kubectl config set-context --current --namespace=test
```

a successfull run will look like this:
```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kubectl config set-context --current --namespace=test
Context "kind-kind-01" modified.
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```

This means that every command running from now will automatically in the 'test' Namespace.

## Step #3: Creating a Pod and running Nginx

### my-first-pod.yaml

We wil create a yaml file called 'my-first-pod.yaml'

```yaml
# Kubernetes API version to cteate an object from the type: Pod.
apiVersion: v1
# Telling kind to create an object from the type: Pod
# "Pod" - the most basic unit that runs containers in k8s.
kind: Pod
# General information about the Pod
metadata:
  # The unique name we'll give the Pod in this cluster
  name: example-pod
  # Labels: help us identify, filer and select the pod later (services for example)
  labels:
    app: my-app
# What Specifications this pod needs to hold
spec:
  # List of containers that will run in this Pod (usually only one)
  containers:
    # The internal name we give this specific container
  - name: my-container
    # The Docker image we want to run 
    # In this case: Nginx in the latest version
    image: nginx:latest
    # Setting the internal ports of the container
    ports:
      # Tells k8s that Nginx is listening to traffic in port 80 
    - containerPort: 80
```

### Tell k8s to create the Pod in our Namespace

To tell k8s to create the Pod in our Namespace we will run this PowerShell command:

```powershell
kubectl apply -f my-first-pod.yaml
```

A successfull run will show the following output:
```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kubectl apply -f my-first-pod.yaml
pod/example-pod created
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```

## Step 4: Test all is running

Check that the Pod is running with the following command:
```powershell
kubectl get pods
```

A running output will look like this:
```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kubectl get pods
NAME          READY   STATUS    RESTARTS   AGE
example-pod   1/1     Running   0          2m42s
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```




<div style="background-color: #f0f4f8; padding: 15px; border-left: 4px solid #0066cc; border-radius: 4px;">
🧠 <b>Why can't I access the new pod from my browser?:</b><br>
In order to open the browser to you're PC you must add a service.
</div>


## Step 5: Adding a service

### Create a yaml file called 'my-first-service.yaml'

We'll create a 'my-first-service.yaml' file

```yaml
# Kubernetes API version for network settings
apiVersion: v1
# Telling kubernetes the network type: in the case 'Service'.
# Service: a network service that routes traffic
kind: Service
metadata:
  # The name we'll call the service
  name: my-nginx-service
spec:
  # Service type: NodePort allows exposing a port outside the cluster through the servers (Nodes).
  type: NodePort
  # The connector: The service will look in the cluster for any pod that has the label "app: my-app" like our pod.
  selector:
    app: my-app
  ports:
    # The port the service itself will listen INSIDE the cluster.
  - port: 80
    # The internal Nginx port inside the Pod, where the traffic will get to in the end.
    targetPort: 80
    # The port of the node: Must be 30002, as this is what we opened in the kind-config.yaml file when creating the cluster.
    nodePort: 30002
```

### Run the service in the cluster

Run the command to start the service in the cluster

```powershell
kubectl apply -f my-first-service.yaml
```

A successfull output will look like this:

```powershell
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01> kubectl apply -f my-first-service.yaml
service/my-nginx-service created
PS C:\Users\Eli Brody\Desktop\l-h-01\k8s\lab-01>
```




### Now you can test from your PC and see Nginx is running 

http://127.0.0.1:8000/
or 
http://localhost:8000/

```html
Welcome to nginx!
...
```


# Understand the network flow we created here!

## How the Network Traffic Flows (The 3 Stations)

Although our Nginx web server runs internally on **Port 80** inside its isolated container, we can access it from our local browser using **Port 8000** (`http://localhost:8000`). 

Here is how the connection works step-by-step, moving through 3 stations:

[Browser: Port 8000] ──> [KinD Cluster: Port 30002] ──> [Nginx Pod: Port 80]


### Station 1: Your PC to the Cluster (Host to Node)
In our `kind-config.yaml` file, we set up a port mapping. We told Docker that any traffic coming into our physical computer on **Port 8000** (`hostPort`) should be automatically forwarded to **Port 30002** (`containerPort`) inside the cluster's virtual server (the Node).

### Station 2: Entering the Cluster via NodePort Service
Inside the cluster, we created a Kubernetes `Service` with `type: NodePort`. This Service listens specifically on **Port 30002** (`nodePort`). As soon as traffic arrives from Station 1, the Service catches it and uses a `selector` to find our Nginx Pod (by looking for the label `app: my-app`).

### Station 3: From the Service to Nginx (Service to Pod)
The Service knows that the Nginx application inside the Pod is listening on its standard **Port 80**. Therefore, the Service takes the traffic from Port 30002 and injects it directly into **Port 80** (`targetPort`) of the Pod. 

---
**Summary:** Port **8000** on your PC connects to Port **30002** in the cluster, which the **NodePort Service** routes directly to Port **80** inside the Pod.
