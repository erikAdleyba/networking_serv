from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Секретный ключ для подписи сессий
DATABASE = 'cards.db'

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

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
            phone TEXT,
            contacts TEXT,
            conversations TEXT,
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

# Главная страница (карточки)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Перенаправляем на страницу входа, если пользователь не авторизован
    return render_template('index.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

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
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных: {e}")
            return jsonify({"error": "Ошибка базы данных"}), 500
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"error": "Логин и пароль обязательны"}), 400

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных: {e}")
            return jsonify({"error": "Ошибка базы данных"}), 500
        finally:
            conn.close()

        if user is None:
            return jsonify({"error": "Пользователь не найден"}), 404

        if not check_password_hash(user[1], password):
            return jsonify({"error": "Неверный пароль"}), 401

        # Сохраняем ID пользователя в сессии
        session['user_id'] = user[0]
        return jsonify({"message": "Успешный вход"}), 200
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем ID пользователя из сессии
    return redirect(url_for('login'))

# Проверка авторизации
@app.route('/check_auth')
def check_auth():
    if 'user_id' not in session:
        return jsonify({"error": "Не авторизован"}), 401
    return jsonify({"message": "Авторизован"}), 200

# Создание карточки
@app.route('/cards', methods=['POST'])
def create_card():
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    data = request.json
    full_name = data.get('full_name').lower()  # Приводим к нижнему регистру
    birth_date = data.get('birth_date')
    interests = data.get('interests', '').lower()  # Приводим к нижнему регистру
    phone = data.get('phone')
    contacts = data.get('contacts', '').lower()  # Приводим к нижнему регистру
    conversations = data.get('conversations', '').lower()  # Приводим к нижнему регистру

    if birth_date and not is_valid_date(birth_date):
        return jsonify({"error": "Неверный формат даты. Используйте формат дд.мм.гггг."}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cards (user_id, full_name, birth_date, interests, phone, contacts, conversations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], full_name, birth_date, interests, phone, contacts, conversations))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    finally:
        conn.close()

    return jsonify({"message": "Card created"}), 201

# Получение карточек
@app.route('/cards', methods=['GET'])
def get_cards():
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cards WHERE user_id = ?', (session['user_id'],))
        cards = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    finally:
        conn.close()

    return jsonify(cards)

# Поиск карточек
@app.route('/cards/search', methods=['GET'])
def search_cards():
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    search_query = request.args.get('query', '').strip().lower()  # Получаем поисковый запрос
    print("Поисковый запрос:", search_query)  # Отладочное сообщение

    if not search_query:
        return jsonify([])  # Если запрос пустой, возвращаем пустой список

    # Разбиваем поисковый запрос на отдельные слова
    search_words = search_query.split()

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Создаем SQL-запрос для поиска по каждому слову
        query = '''
            SELECT * FROM cards 
            WHERE user_id = ? 
            AND (
        '''
        params = [session['user_id']]

        for i, word in enumerate(search_words):
            if i > 0:
                query += ' OR '
            query += '(LOWER(full_name) LIKE ? OR LOWER(interests) LIKE ? OR LOWER(conversations) LIKE ?)'
            params.extend([f'%{word}%', f'%{word}%', f'%{word}%'])

        query += ')'

        cursor.execute(query, params)
        cards = cursor.fetchall()
        print("Найденные карточки:", cards)  # Отладочное сообщение
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    finally:
        conn.close()

    return jsonify(cards)

# Редактирование карточки
@app.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    data = request.json
    full_name = data.get('full_name').lower()  # Приводим к нижнему регистру
    birth_date = data.get('birth_date')
    interests = data.get('interests', '').lower()  # Приводим к нижнему регистру
    phone = data.get('phone')
    contacts = data.get('contacts', '').lower()  # Приводим к нижнему регистру
    conversations = data.get('conversations', '').lower()  # Приводим к нижнему регистру

    if birth_date and not is_valid_date(birth_date):
        return jsonify({"error": "Неверный формат даты. Используйте формат дд.мм.гггг."}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cards
            SET full_name = ?, birth_date = ?, interests = ?, phone = ?, contacts = ?, conversations = ?
            WHERE id = ? AND user_id = ?
        ''', (full_name, birth_date, interests, phone, contacts, conversations, card_id, session['user_id']))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    finally:
        conn.close()

    return jsonify({"message": "Card updated"}), 200

# Удаление карточки
@app.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 401

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cards WHERE id = ? AND user_id = ?', (card_id, session['user_id']))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    finally:
        conn.close()

    return jsonify({"message": "Card deleted"}), 200

# Запуск сервера
if __name__ == '__main__':
    init_db()
    app.run(debug=True)