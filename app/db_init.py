import psycopg2
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Замените 'your_username' и 'your_password' на ваши реальные данные
DB_CONFIG = {
    'dbname': 'networking_service',
    'user': 'your_username',  # Ваше имя пользователя для базы данных
    'password': 'your_password',  # Ваш пароль для базы данных
    'host': 'localhost',
    'port': '5432'
}

@contextmanager
def get_db_connection():
    connection = None
    try:
        logger.debug(f"Attempting to connect to database with config: {DB_CONFIG}")
        connection = psycopg2.connect(**DB_CONFIG)
        logger.debug("Database connection established.")
        yield connection
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
    finally:
        if connection:
            connection.close()
            logger.debug("Database connection closed.")

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
        finally:
            cursor.close()