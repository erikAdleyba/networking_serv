from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = 'auth.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    password_hash = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Пользователь уже существует"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Пользователь зарегистрирован"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not check_password_hash(user[1], password):
        return jsonify({"error": "Неверный пароль"}), 401

    return jsonify({"user_id": user[0]}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)