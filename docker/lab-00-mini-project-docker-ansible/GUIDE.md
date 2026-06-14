# 🚀 Automated Infrastructure Guide: Docker & Ansible Orchestration

This guide details the step-by-step execution, raw configuration files, and deployment lifecycle of a complete automated multi-node DevSecOps architecture utilizing **Docker**, **Ansible**, **Flask**, and **PostgreSQL**.

---

## 🗂️ Step 1: Directory Structure & Key Generation

Before writing configuration files, the target directory schema must be established exactly as follows:

```text
mini-project/
├── ansible/
│   ├── deploy.yml
│   ├── docker-compose.yml
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

DB_HOST = os.getenv("DB_HOST", "ansible-slave-2")
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")

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
FROM python:3.11-slim

WORKDIR /app

# Install dependencies early to optimize layer caching
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/users || exit 1

CMD ["python", "src/app.py"]

```

### 📄 `app/docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    build: .
    image: elibrodyisrael/python-app:latest
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=${DB_HOST}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    networks:
      - app-net

networks:
  app-net:
    external: true
    name: ansible_infra-network

```

---

## 🐳 Step 3: Custom Node Base Images (`ansible-*`)

Both master and slave units utilize standardized **Ubuntu OS** baselines hardened for automation transport layers.

### 📄 `ansible-master/Dockerfile`

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ansible \
    openssh-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establish runtime SSH key layouts
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
COPY ansible-key /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Suppress host key verification safety prompts for programmatic flows
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]

```

### 📄 `ansible-slave/Dockerfile`

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure standard openSSH daemon parameters
RUN mkdir /var/run/sshd
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Mount public key identity into runtime authority profile
COPY ansible-key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# Install Docker CLI binaries inside the slave so it can build/run native host commands
RUN curl -fsSL [https://get.docker.com](https://get.docker.com) | sh

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

```

---

## 🐘 Step 4: Storage & Visualization Layer (`database/`)

### 📄 `database/docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: postgres-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-net

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin-ui
    ports:
      - "8080:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=adminpassword
    networks:
      - app-net

volumes:
  pgdata:

networks:
  app-net:
    external: true
    name: ansible_infra-network

```

---

## 🏗️ Step 5: Global Infrastructure Orchestration (`ansible/`)

This acts as the root architecture framework, establishing the multi-node lab environment on your host computer.

### 📄 `ansible/docker-compose.yml`

```yaml
version: '3.8'

services:
  ansible-master:
    image: elibrodyisrael/ansible-master:latest
    container_name: ansible-master
    volumes:
      - ..:/workspace
    networks:
      - infra-network

  ansible-slave-1:
    image: elibrodyisrael/ansible-slave:latest
    container_name: ansible-slave-1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - infra-network

  ansible-slave-2:
    image: elibrodyisrael/ansible-slave:latest
    container_name: ansible-slave-2
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - infra-network

networks:
  infra-network:
    name: ansible_infra-network
    driver: bridge

```

### 📄 `ansible/inventory.ini`

```ini
[app_servers]
ansible-slave-1 ansible_user=root

[db_servers]
ansible-slave-2 ansible_user=root

```

### 📄 `ansible/deploy.yml`

```yaml
---
- name: Multi-Node Infrastructure Automated Orchestration Pipeline
  hosts: all
  gather_facts: no
  tasks:
    - name: Assert Target Transport State via SSH Ping
      ansible.builtin.ping:

- name: Provision Application Server Infrastructure Instance
  hosts: app_servers
  tasks:
    - name: Synchronize Runtime Configurations to App Node
      ansible.builtin.copy:
        src: /workspace/app/
        dest: /opt/app/
        mode: '0755'

    - name: Trigger Remote Docker Orchestration Instance
      ansible.builtin.shell: |
        cd /opt/app
        export DB_HOST=ansible-slave-2
        export POSTGRES_DB=mydatabase
        export POSTGRES_USER=myuser
        export POSTGRES_PASSWORD=mysecretpassword
        docker compose down
        docker compose up -d --build
      async: 300
      poll: 10

- name: Provision Relational Database Storage Engine
  hosts: db_servers
  tasks:
    - name: Synchronize Storage Definitions to Database Node
      ansible.builtin.copy:
        src: /workspace/database/
        dest: /opt/database/
        mode: '0755'

    - name: Trigger Remote Datastore Runtime Initialization
      ansible.builtin.shell: |
        cd /opt/database
        export POSTGRES_DB=mydatabase
        export POSTGRES_USER=myuser
        export POSTGRES_PASSWORD=mysecretpassword
        docker compose down
        docker compose up -d
      async: 300
      poll: 10

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
cd /workspace/ansible

# Execute the automation playbook 
ansible-playbook -i inventory.ini deploy.yml

```

### 4. Operational Health Validation

Open your web browser on your native host operating system and query the network links:

* **Application Health Check Endpoint:** `http://localhost:5000/users`
* **Database Management UI Panel:** `http://localhost:8080` (Log in with `admin@admin.com` / `adminpassword`)

```