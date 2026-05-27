from flask import Flask, jsonify, request
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

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS greetings (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "backend"})

@app.route("/greetings", methods=["GET"])
def get_greetings():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, message, created_at FROM greetings ORDER BY created_at DESC;")
        rows = cur.fetchall()
        greetings = [{"id": r[0], "name": r[1], "message": r[2], "created_at": str(r[3])} for r in rows]
        return jsonify({"greetings": greetings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/greetings", methods=["POST"])
def add_greeting():
    try:
        data = request.get_json()
        name = data.get("name")
        message = data.get("message")
        if not name or not message:
            return jsonify({"error": "name and message required"}), 400
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO greetings (name, message) VALUES (%s, %s) RETURNING id;", (name, message))
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id, "name": name, "message": message}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/greetings/<int:greeting_id>", methods=["DELETE"])
def delete_greeting(greeting_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM greetings WHERE id = %s;", (greeting_id,))
        conn.commit()
        return jsonify({"message": "deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)