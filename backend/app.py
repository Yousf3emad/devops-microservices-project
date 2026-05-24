from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "password")
    )

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "backend"})

@app.route("/api/users")
def get_users():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users;")
        rows = cur.fetchall()
        users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

    