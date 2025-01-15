from db_init import get_db_cursor
import bcrypt
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def create_table():
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL
                    )
                ''')
                logger.debug("Users table created or already exists.")
            except Exception as e:
                logger.error(f"Error creating users table: {e}")

    @staticmethod
    def register(username, password):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
                logger.debug(f"User {username} registered successfully.")
            except Exception as e:
                logger.error(f"Error registering user: {e}")

    @staticmethod
    def login(username, password):
        with get_db_cursor() as cursor:
            try:
                cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                    logger.debug(f"User {username} logged in successfully.")
                    return user[0]
                else:
                    logger.debug(f"Login failed for user {username}.")
                    return None
            except Exception as e:
                logger.error(f"Error during login: {e}")
                return None

class Contact:
    @staticmethod
    def create_table():
        with get_db_cursor(commit=True) as cursor:
            try:
                # Создание таблицы контактов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contacts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        full_name VARCHAR(100) NOT NULL,
                        birth_date DATE,
                        phone_number VARCHAR(15),
                        interests TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                logger.debug("Contacts table created or already exists.")

                # Создание таблицы бесед
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        contact_id INTEGER REFERENCES contacts(id),
                        conversation_date DATE,
                        last_conversation TEXT
                    )
                ''')
                logger.debug("Conversations table created or already exists.")
            except Exception as e:
                logger.error(f"Error creating tables: {e}")

    @staticmethod
    def add_contact(user_id, full_name, birth_date, phone_number, interests):
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('''
                    INSERT INTO contacts (user_id, full_name, birth_date, phone_number, interests)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (user_id, full_name, birth_date, phone_number, interests))
                contact_id = cursor.fetchone()[0]
                logger.debug(f"Contact added for user {user_id} with ID {contact_id}.")
                return contact_id
            except Exception as e:
                logger.error(f"Error adding contact: {e}")

    @staticmethod
    def add_conversation(contact_id, conversation_date, last_conversation):
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('''
                    INSERT INTO conversations (contact_id, conversation_date, last_conversation)
                    VALUES (%s, %s, %s)
                ''', (contact_id, conversation_date, last_conversation))
                logger.debug(f"Conversation added for contact {contact_id}.")
            except Exception as e:
                logger.error(f"Error adding conversation: {e}")

    @staticmethod
    def get_contacts(user_id):
        with get_db_cursor() as cursor:
            try:
                cursor.execute('SELECT * FROM contacts WHERE user_id = %s', (user_id,))
                contacts = cursor.fetchall()
                logger.debug(f"Retrieved contacts for user {user_id}.")
                return contacts
            except Exception as e:
                logger.error(f"Error retrieving contacts: {e}")
                return []

    @staticmethod
    def get_conversations(contact_id):
        with get_db_cursor() as cursor:
            try:
                cursor.execute('SELECT * FROM conversations WHERE contact_id = %s', (contact_id,))
                conversations = cursor.fetchall()
                logger.debug(f"Retrieved conversations for contact {contact_id}.")
                return conversations
            except Exception as e:
                logger.error(f"Error retrieving conversations: {e}")
                return []

    @staticmethod
    def edit_contact(contact_id, full_name, birth_date, phone_number, interests):
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('''
                    UPDATE contacts
                    SET full_name = %s, birth_date = %s, phone_number = %s, interests = %s
                    WHERE id = %s
                ''', (full_name, birth_date, phone_number, interests, contact_id))
                logger.debug(f"Contact {contact_id} updated successfully.")
            except Exception as e:
                logger.error(f"Error updating contact: {e}")

    @staticmethod
    def delete_contact(contact_id):
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute('DELETE FROM contacts WHERE id = %s', (contact_id,))
                logger.debug(f"Contact {contact_id} deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting contact: {e}")

    @staticmethod
    def search_contacts(user_id, query):
        with get_db_cursor() as cursor:
            try:
                cursor.execute('''
                    SELECT * FROM contacts 
                    WHERE user_id = %s AND (
                        full_name ILIKE %s OR 
                        interests ILIKE %s OR 
                        TO_CHAR(birth_date, 'YYYY-MM-DD') ILIKE %s
                    )
                ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
                contacts = cursor.fetchall()
                logger.debug(f"Search results for user {user_id}: {contacts}")
                return contacts
            except Exception as e:
                logger.error(f"Error searching contacts: {e}")
                return []