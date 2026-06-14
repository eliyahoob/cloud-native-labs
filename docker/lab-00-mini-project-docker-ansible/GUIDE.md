# Mini Project - Eli's Change Log

# 🚀 DevOps Automation Mini-Project Guide

This guide details the step-by-step execution and configuration of a complete automated infrastructure using **Docker**, **Ansible**, **Flask**, and **PostgreSQL**.

---

## 🛠️ Step 1: Project Setup & Repository

1. **Initialize Git Repository:** Created a local repository and pushed to GitHub.

## Step #1 Create folder hierarchy 

ansible
ansible-master
ansible-slave
app
|_ src
database



### The following files will be addes later into these folders

ansible
|_ deploy.yml
|_ docker-compose.yml
|_ inventory.ini
ansible-master
|_ Dockerfile
|_ id_rsa
ansible-slave
|_ Dockerfile
is_rsa.pub
app
|_ src
    |_ app.py
    |_ requirements.txt
|_ docker-compose.yml
|_ Dockerfile
database
|_ docker-compose.yml


---

## 🐍 Step 2: Flask Application Development (`app/`)

A REST API backend built using Python Flask to handle user data.

* **Endpoints Implemented:**
* `GET /users`: Returns a JSON list of all registered users.
* `POST /users`: Registers a new user with `username`, `email`, and `password`.


* **Security & Environment:** Hardcoded secrets were eliminated. Database credentials, host, and port are injected dynamically at runtime via Docker environment variables (`.env`).

---

## 🔑 Step 3: Secure SSH Key Generation

To establish automated, passwordless trust between the automation master and the host servers:

1. Generated a secure SSH key pair locally.
2. **Key Distribution Strategy:**
* **Private Key:** Mounted securely inside the `ansible-master` container.
* 
**Public Key:** Injected into `ansible-slave` containers via `authorized_keys`.




3. **Best Practice Violation Avoidance:** Keys are **not** baked into the Docker images during the build phase. Instead, they are dynamically mapped at runtime using standard Docker Volumes.

---

## 🐳 Step 4: Custom Docker Images (Based on Ubuntu)

Custom environments built on top of **Ubuntu OS** as strictly required by the project specifications.

### 1. Ansible Master (`ansible-master/Dockerfile`)

* **Base OS:** Ubuntu.
* **Tools Installed:** Ansible, OpenSSH client, and Git.
* **Purpose:** Acts as the central controller orchestration engine.

### 2. Ansible Slave (`ansible-slave/Dockerfile`)

* **Base OS:** Ubuntu.
* **Tools Installed:** OpenSSH Server (`sshd`), Python3 (required for Ansible to execute tasks), and Docker Compose.
* **Purpose:** Runs a continuous SSH daemon to accept configuration payloads from the Master.

### 📤 Building and Publishing to DockerHub

The custom images were built locally and pushed to public repositories:

```bash
docker build -t elibrodyisrael/ansible-master:latest ./ansible-master
docker build -t elibrodyisrael/ansible-slave:latest ./ansible-slave

docker push elibrodyisrael/ansible-master:latest
docker push elibrodyisrael/ansible-slave:latest

```

---

## 🏗️ Step 5: Infrastructure Orchestration (`ansible/`)

The core architecture definition mapping out the three virtual infrastructure nodes using `docker-compose.yml`.

### 🖥️ Node Architecture

* **`ansible-master`**: Runs the automation engine.
* **`ansible-slave-1`**: Target Application node running the Python Flask API.
* **`ansible-slave-2`**: Target Database node running PostgreSQL and pgAdmin 4 for UI management.

### ⚙️ Automation Implementation

* **`inventory.ini`**: Lists the target managed slaves using Docker internal network routing.
* **`deploy.yml`**: The central Ansible Playbook executing the automation tasks. It handles:
1. Testing SSH connectivity via standard ping.


2. Pulling deployment configurations from the codebase.
3. Orchestrating and spinning up the respective application and database instances using Docker Compose directly on the target environments.



---

## 🚀 Execution Commands

To execute the entire deployment lifecycle from scratch, run the following commands inside the initialized master controller:

```bash
# 1. Access the master automation control panel
docker exec -it ansible-master bash

# 2. Navigate to the orchestration control directory
cd /mini-project/ansible

# 3. Fire the automation playbook
ansible-playbook -i inventory.ini deploy.yml

```














______________________________________________








## Step #2 Create Flask app


#### /app/src/app.py  

app
|_ src
    |_ app.py
    |_ requirements.txt

```python
import os
import time
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Fetch database credentials from environment variables (No hardcoded secrets)
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword") # Should be set as envieronment variable for security! (Or Docker secrets. Can not do now due to time constraints, but should be done in production!)


def get_db_connection():
    """Connects to the PostgreSQL database with retry logic."""
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
            print("Database not ready yet, retrying in 2 seconds...")
            time.sleep(2)


@app.route("/users", methods=["GET"])
def get_users():
    """Fetches and returns all users from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Create table if it doesn't exist yet
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
    """Receives JSON data and inserts a new user into the database."""
    data = request.get_json()

    if not data or "username" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s);",
        (data["username"], data["email"], data["password"]),
    )
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"message": "User created successfully"}), 201


if __name__ == "__main__":
    # Listen on port 5000 as required
    app.run(host="0.0.0.0", port=5000)
```

#### Flask Quick Start Guide:
https://flask.palletsprojects.com/en/stable/quickstart/


## Step 3 


#### Create Dockerfile following this example:
https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

#### Create a docker-compose orchestration file:
https://docs.docker.com/compose/gettingstarted/
(Sections 5 & 6 discuss .env and .dockerignore files. Maybe will get back to this part of the project again at the end and will fix hardcoded credentials)

## Generate SSH keys

Generate SSH key https://docs.hpc.oregonstate.edu/cqls/connecting/sshkey/
* Private key in ansible-master folder
* Public key in ansible-slave folder

## Create ansible-master image

Create dockerfile (again - https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile)

## Create ansible-slave image

Create dockerfile (again - https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile)


## Build Images
https://docs.docker.com/get-started/introduction/build-and-push-first-image/

### Building the Docker Image done with these command (in the folder the Dockerfile is in)
docker build -t elibrodyisrael/ansible-master:latest .
docker build -t elibrodyisrael/ansible-slave:latest .

## Push Images to Docker Hub

### Push to publich repository is done with these commands

https://docs.docker.com/get-started/introduction/build-and-push-first-image/

docker login
docker push elibrodyisrael/ansible-master:latest
docker push elibrodyisrael/ansible-slave:latest

## Docker Images Public URLs:
https://hub.docker.com/r/elibrodyisrael/ansible-master
https://hub.docker.com/r/elibrodyisrael/ansible-slave

## Database environment

### PostgreSql
https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/
Official Postgress DockerHub page:
https://hub.docker.com/_/postgres


### PGadmin
https://docs.docker.com/guides/pgadmin/
Official PGadmin DockerHub page:
https://hub.docker.com/r/dpage/pgadmin4


## Main Ansible environment setup

### In 'ansible' folder:
* Create 'docker-compose.yml' file with the 3 servers (Ansible-Master, Ansible-Slave-1, Ansible-Slave-2)
https://docs.docker.com/compose/gettingstarted/

* Create 'inventory.ini' file with the list of servers for ansible deployment
https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html

* Create a 'deploy.yml' file with the full actions for the ansible automation
https://github.com/mattupstate/ansible-tutorial/blob/master/devops/deploy.yml

### To run this (activate the playbook), use the following command from the ansible-master container

#### Login to the ansible master contianer:
docker exec -it ansible-master bash

#### Run ansible playbook
cd /mini-project-2nd-try/ansible
ansible-playbook -i inventory.ini deploy.yml




#### Environment virables: 
https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/

#### Docker secrets:
https://forums.docker.com/t/understanding-security-implications-of-secrets-vs-env-vars-in-docker-compose/145903

