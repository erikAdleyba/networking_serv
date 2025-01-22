from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = 'cards.db'

# Инициализация базы данных
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            birth_date TEXT,
            interests TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Валидация даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Пользователь уже существует"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Пользователь зарегистрирован"}), 201

# Вход
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user[1], password):
        return jsonify({"error": "Неверный логин или пароль"}), 401

    return jsonify({"message": "Успешный вход", "user_id": user[0]}), 200

# Создание карточки
@app.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    user_id = data.get('user_id')
    full_name = data.get('full_name')
    birth_date = data.get('birth_date')
    interests = data.get('interests')

    if not user_id:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    if birth_date and not is_valid_date(birth_date):
        return jsonify({"error": "Неверный формат даты. Используйте формат дд.мм.гггг."}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cards (user_id, full_name, birth_date, interests) VALUES (?, ?, ?, ?)',
                   (user_id, full_name, birth_date, interests))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card created"}), 201

# Получение карточек
@app.route('/cards', methods=['GET'])
def get_cards():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cards WHERE user_id = ?', (user_id,))
    cards = cursor.fetchall()
    conn.close()
    return jsonify(cards)

# Редактирование карточки
@app.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    data = request.json
    user_id = data.get('user_id')
    full_name = data.get('full_name')
    birth_date = data.get('birth_date')
    interests = data.get('interests')

    if not user_id:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    if birth_date and not is_valid_date(birth_date):
        return jsonify({"error": "Неверный формат даты. Используйте формат дд.мм.гггг."}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE cards
        SET full_name = ?, birth_date = ?, interests = ?
        WHERE id = ? AND user_id = ?
    ''', (full_name, birth_date, interests, card_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card updated"}), 200

# Удаление карточки
@app.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cards WHERE id = ? AND user_id = ?', (card_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card deleted"}), 200

# Запуск сервера
if __name__ == '__main__':
    init_db()
    app.run(debug=True)