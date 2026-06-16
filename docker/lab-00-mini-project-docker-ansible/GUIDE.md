# 🚀 Automated Infrastructure Guide: Docker & Ansible Orchestration

This guide details the step-by-step execution, raw configuration files, and deployment lifecycle of a complete automated multi-node DevSecOps architecture utilizing **Docker**, **Ansible**, **Flask**, and **PostgreSQL**.

---

## 🗂️ Step 1: Directory Structure & Key Generation

Before writing configuration files, the target directory schema must be established exactly as follows:


```text
mini-project/
├── ansible/
├── ansible-master/
├── ansible-slave/
├── app/
│   └── src/
└── database/
```

Folders can be created via CLI (PowerShell):
```PowerShell
mkdir ansible, ansible-master, ansible-slave, app\src, database
```

The  final structure (folders and files) will look like this:
```text
mini-project/
├── .gitignore
├── .env
├── ansible/
│   ├── .env
│   ├── deploy.yml
│   └── inventory.ini
├── ansible-master/
│   ├── Dockerfile
│   └── ansible-key
├── ansible-slave/
│   ├── Dockerfile
│   └── ansible-key.pub
├── app/
│   ├── src/
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── docker-compose.yml
│   └── Dockerfile
└── database/
    └── docker-compose.yml
```



### 🔐 DevSecOps Security Configurations
### 📄 `.gitignore`
Create a **.gitignore** file in the root directory (mini-project/) to ensure no sensitive credentials, keys, or locally configured variables ever leak to public version control systems:
```plaintext
# ---------------------------------------------------------------------------
# Environmental Secrets (Crucial to block to prevent data leaks)
# ---------------------------------------------------------------------------
/ansible/.env
/.env

# ---------------------------------------------------------------------------
# Environmental keys for SSH login (Crucial to block to prevent data leaks)
# ---------------------------------------------------------------------------
ansible-key
ansible-key.pub
```
### 📄 `.env`
Create a .env file directly **in the project root folder and inside the ansible/ folder** (As this project uses DinD this is the secure solution I've deciced to go with. There are other ways too):
```plaintext
POSTGRES_DB=mydatabase
POSTGRES_USER=mysecureuser
POSTGRES_PASSWORD=SuperSecurePassword2026!
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=adminpassword
```



### 🔑 Cryptographic Authentication Setup

To establish secure, passwordless execution between the master controller and target nodes without hardcoding credentials into images, generate an RSA key pair in the root directory:

```bash
ssh-keygen -t rsa -b 2048 -f ./ansible-key -N ""

```

* Move the private key (`ansible-key`) directly into `ansible-master/`.
* Move the public key (`ansible-key.pub`) directly into `ansible-slave/`.

---

## 🐍 Step 2: Application Layer Backend (`app/`)

The backend is an enterprise-ready, stateless REST API running Python Flask. It features automated schema migration on boot and aggressive database connection retry handlers.

### 📄 `app/src/requirements.txt`

```text
flask==3.0.3
psycopg2-binary==2.9.9

```

### 📄 `app/src/app.py`

```python
import os
import time
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def get_db_connection():
    """Establishes connection to PostgreSQL with fault-tolerant retry logic."""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor,
            )
            return conn
        except psycopg2.OperationalError:
            print("Database layer unavailable. Retrying in 2 seconds...")
            time.sleep(2)

@app.route("/users", methods=["GET"])
def get_users():
    """Retrieves all data profiles dynamically from the storage engine."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50), email VARCHAR(50), password VARCHAR(50));"
    )
    conn.commit()

    cur.execute("SELECT id, username, email FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users), 200

@app.route("/users", methods=["POST"])
def create_user():
    """Ingests data payloads and commits record transactions safely."""
    data = request.get_json()
    if not data or "username" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "Bad Request: Missing payload components"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s);",
        (data["username"], data["email"], data["password"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User configuration committed successfully"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

```

### 📄 `app/Dockerfile`

```dockerfile
# OS: Slim environment running Python 3.11 slim									   
FROM python:3.11-slim
											
WORKDIR /app

# Install dependencies early to optimize layer caching
COPY src/requirements.txt .

# Install the libraries Python needs 									 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container														
COPY src/ ./src

# Expose port 5000				  
EXPOSE 5000

# Run health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/users || exit 1

# Run the application					 
CMD ["python", "src/app.py"]
```

### 📄 `app/docker-compose.yml`

```yaml
version: '3.8'

services:
  web-app:
    build: .
    ports:
     - "5000:5000"
    environment:
      DB_HOST: postgres-db
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    extra_hosts:
      - "host.docker.internal:host-gateway" # Allow the container to access the host machine using "host.docker.internal"
    networks:
      - ansible_project-network # Join the Ansible virtual network

networks:
  ansible_project-network:
    external: true # Use the existing Ansible virtual network. Tell Docker this virtual network is already created outside of this docker-compose file
```

---

## 🐳 Step 3: Custom Node Base Images (`ansible-*`)

Both master and slave units utilize standardized **Ubuntu OS** baselines hardened for automation transport layers.

### 📄 `ansible-master/Dockerfile`

```dockerfile
# Ubuntu OS	   
FROM ubuntu:22.04

# Tell Ubuntu: Do not show interactive menus.											 
ENV DEBIAN_FRONTEND=noninteractive

# Commands: update system, install: Ansible, SSH tools, GIT.															
RUN apt-get update && apt-get install -y \
    ansible \
    openssh-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establish runtime SSH key layouts (Create the .ssh directory inside the master container for root user)
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
# Copy the private key (the key itself) into the Master's SSH directory																	   
COPY ansible-key /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Disable SSH strict host key checking (prevents manual "yes/no" prompts)
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

# Set the default working directory where playbooks will sit															
WORKDIR /ansible
CMD ["tail", "-f", "/dev/null"]
```

### 📄 `ansible-slave/Dockerfile`

```dockerfile
#OS: Ubuntu
FROM ubuntu:22.04
						  
# Update system and install SSH
RUN apt-get update && apt-get install -y \
    openssh-server \			 
    curl \
    && mkdir /var/run/sshd

# Set SSH key for root user
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Copy the public key into the "authorized_keys" file
COPY ansible-key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# Configure SSH daemon to permit root login and public key auth
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Install Docker (in the Ansible-Slave Docker container)
RUN curl -fsSL https://get.docker.com | sh

# Open SSH port
EXPOSE 22

# Run SSH service in the backround
CMD ["/usr/sbin/sshd", "-D"]

```

---

## 🐘 Step 4: Storage & Visualization Layer (`database/`)

### 📄 `database/docker-compose.yml`

```yaml
# Docker compose engine version 3.8
version: '3.8'

# Main block containing services (containers) to run
services:
  db:
    # Official PostgreSQL image from Docker Hub                                           
    image: postgres:15-alpine
    container_name: postgres-db    
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB} 

    volumes:
      - pgdata:/var/lib/postgresql/data
                                                             
    networks:
      - ansible_project-network


# Use PGADMIN as the service graphic infrastructure management tool           
  pgadmin:
             
    image: dpage/pgadmin4:latest
    container_name: pgadmin-ui                                                
    ports:
      - "8080:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD}
    networks:
      - ansible_project-network


# Offical setting of the volume we've used in db service                                                        
volumes:
  pgdata:

networks:
  ansible_project-network:
    external: true # tells docker to use existing network created by ansible playbook, not to create new one
```

---

## 🏗️ Step 5: Global Infrastructure Orchestration (`ansible/`)

This acts as the root architecture framework, establishing the multi-node lab environment on your host computer.

### 📄 `ansible/docker-compose.yml`

```yaml
version: '3.8'

services:
  # Server #1 Ansible Master
  ansible-master:
    image: elibrodyisrael/ansible-master:latest
    # restart: always
    container_name: ansible-master
    # ports:
    #   - "5432:5432"
    volumes:
      - ../:/lab-00-mini-project-docker-ansible
    networks:
      - ansible_project-network
    depends_on:
      - ansible-slave-1
      - ansible-slave-2
  
  # Server #2 Ansible Slave 1
  ansible-slave-1:
    image: elibrodyisrael/ansible-slave:latest
    # restart: always
    container_name: ansible-slave-1
    networks:
      - ansible_project-network
    volumes:
      # Alloes Ubuntu container use the docker on the host machine (Docker in Docker)
      - /var/run/docker.sock:/var/run/docker.sock                  
  ansible-slave-2:
    image: elibrodyisrael/ansible-slave:latest
    # restart: always
    container_name: ansible-slave-2
    networks:
      - ansible_project-network
    volumes:
      # Alloes Ubuntu container use the docker on the host machine (Docker in Docker)
      - /var/run/docker.sock:/var/run/docker.sock                   
networks:
                
  ansible_project-network:
    driver: bridge
```

### 📄 `ansible/inventory.ini`

```ini
[app_servers]
ansible-slave-1 ansible_user=root ansible_ssh_private_key_file=/root/.ssh/id_rsa

[db_servers]
ansible-slave-2 ansible_user=root ansible_ssh_private_key_file=/root/.ssh/id_rsa
```

### 📄 `ansible/deploy.yml`

```yaml
---
- name: Multi-Node Infrastructure Automated Orchestration Pipeline
  hosts: all
  tasks:
    # Tasks for the applicatio server (ansible-slave-1)
    - name: Deploy Phtyon API on Application Server
      block:
        - name: Create app directory on Slave 1
          file:
            path: /opt/app
            state: directory

        - name: Copy App files from local PC to Slave 1
          copy:
            src: /lab-00-mini-project-docker-ansible/app/
            dest: /opt/app/
            
        - name: Copy .env file to Slave 1 root (for Docker Compose relative path)
          copy:
            src: .env
            dest: /opt/app/.env

        - name: Start Python App Container using Docker Compose
          command: docker compose up -d --build
          args:
            chdir: /opt/app
      when: inventory_hostname == 'ansible-slave-1'

    # Tasks for the database server (ansible-slave-2)
    - name: Deploy PostgreSQL & pgAdmin on Database Server
      block:
        - name: Create database directory on Slave 2
          file:
            path: /opt/database
            state: directory

        - name: Copy Database files from local PC to Slave 2
          copy:
            src: /lab-00-mini-project-docker-ansible/database/
            dest: /opt/database/
            
        - name: Copy .env file to Slave 2 root (for Docker Compose relative path)
          copy:
            src: .env
            dest: /opt/database/.env

        - name: Start Database Containers             
          command: docker compose up -d
          args:
            chdir: /opt/database
      when: inventory_hostname == 'ansible-slave-2'
```

---

## 🚦 Step 6: Compilation & Verification Run

### 1. Build and Publish Base Nodes (Executed Once Locally)

```bash
docker build -t elibrodyisrael/ansible-master:latest ./ansible-master
docker build -t elibrodyisrael/ansible-slave:latest ./ansible-slave

docker login
docker push elibrodyisrael/ansible-master:latest
docker push elibrodyisrael/ansible-slave:latest

```

### 2. Stand Up the Lab Simulation Cluster

```bash
cd ansible
docker compose up -d

```

### 3. Initiate the Automated Configuration Deployment Engine

```bash
# Exec into the running master controller box
docker exec -it ansible-master bash

# Navigate inside the mounted playbook project scope
cd /lab-00-mini-project-docker-ansible/ansible

# Execute the automation playbook 
ansible-playbook -i inventory.ini deploy.yml

```

### 4. Operational Health Validation

Open your web browser on your native host operating system and query the network links:

* **Application Health Check Endpoint:** `http://localhost:5000/users`
* **Database Management UI Panel:** `http://localhost:8080` (Log in with the credentials specified in your .env file)


## 🧹 Step 7: Project Teardown & Environment Cleanup

Here is how to completely stop, clean, and remove all infrastructure components created during this lab.

### 1. Stop and Remove All Containers
Run the following combined command from your project root folder to gracefully stop and remove containers across all components:
```powershell
cd ansible && docker compose down && cd ../app && docker compose down && cd ../database && docker compose down
```

> **💡 SUCCESS TOOL TIP (PowerShell v7+):**
> If you are using an old version of Powershell (older than 7), you can use the the older chain:
> 
> cd ansible; docker compose down; cd ../app; docker compose down; cd ../database; docker compose down 
>
> To upgrade to powershell v7+ visit: https://aka.ms/Powershell7


---

### 2. View and Delete Persistent Volumes

During this lab, PostgreSQL was configured with persistent storage. To list and remove the project volume:

* **View existing volumes:**

```bash
  docker volume ls

```

* **Delete the database volume:**

```bash
  docker volume rm database_pgdata

```

---

### 3. Deep Cleanup: What Did We Actually Create?

Instead of a generic wipe, here is exactly what this project built in your Docker environment and how to remove each specific component:

#### 🔹 Dedicated Docker Network

Ansible created an isolated network called `ansible_project-network` to bridge the app and database containers.

* **Remove it:**

```bash
  docker network rm ansible_project-network

```

#### 🔹 Custom Built Images

We built custom Docker images for our management nodes and our application.

* **Remove the Lab Infrastructure Images:**

```bash
  docker rmi elibrodyisrael/ansible-master:latest
  docker rmi elibrodyisrael/ansible-slave:latest

```

* **Remove the Python App Image:**

```bash
  docker rmi app-web-app

```

#### 🔹 Unused Cache & Dangling Layers

To ensure your local disk is 100% clean from build caches and stopped container leftovers:

```bash
docker system prune -f

```