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
