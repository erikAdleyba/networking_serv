from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from models import User, Contact
from bcrypt import gensalt, hashpw, checkpw
import logging
import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PORT = 8080

# Настройка Jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def _parse_POST_data(self):
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length).decode('utf-8')
        postvars = parse_qs(post_data)
        return postvars

    def do_GET(self):
        logger.debug(f"Handling GET request for path: {self.path}")
        path = urlparse(self.path).path
        if path == '/register':
            self._serve_template('register.html', {})
        elif path == '/login':
            self._serve_template('login.html', {})
        elif path == '/dashboard':
            user_id = self._get_user_id_from_session()
            contacts = Contact.get_contacts(user_id) if user_id else []
            self._serve_dashboard(contacts)
        elif path == '/add_contact':
            self._serve_template('add_contact.html', {})
        elif path.startswith('/static/'):
            self._serve_static(path[8:])
        else:
            self._serve_template('base.html', {})

    def do_POST(self):
        logger.debug(f"Handling POST request for path: {self.path}")
        postvars = self._parse_POST_data()
        if self.path == '/register':
            self._handle_register(postvars)
        elif self.path == '/login':
            self._handle_login(postvars)
        elif self.path == '/add_contact':
            self._handle_add_contact(postvars)
        elif self.path == '/edit_contact':
            self._handle_edit_contact(postvars)
        elif self.path == '/delete_contact':
            self._handle_delete_contact(postvars)
        elif self.path == '/search':
            self._handle_search(postvars)

    def _serve_template(self, template_path, context):
        logger.debug(f"Serving template: {template_path}")
        try:
            template = env.get_template(template_path)
            rendered_html = template.render(context)
            self._set_headers()
            self.wfile.write(rendered_html.encode('utf-8'))
        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}")
            self._set_headers(status=404)
            self.wfile.write(b'Template not found')
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            self._set_headers(status=500)
            self.wfile.write(b'Internal Server Error')

    def _serve_static(self, static_path):
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        static_file_path = os.path.join(static_dir, static_path)
        if os.path.exists(static_file_path):
            self._set_headers(content_type=self._get_mime_type(static_path))
            with open(static_file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            logger.error(f"Static file not found: {static_file_path}")
            self._set_headers(status=404)
            self.wfile.write(b'Static file not found')

    def _get_mime_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript'
        }
        return mime_types.get(ext, 'application/octet-stream')

    def _serve_dashboard(self, contacts):
        logger.debug("Serving dashboard")
        user_id = self._get_user_id_from_session()
        context = {
            'user_id': user_id,
            'contacts': contacts,
            'messages': self._get_flashed_messages()
        }
        template = env.get_template('dashboard.html')
        rendered_html = template.render(context)
        self._set_headers()
        self.wfile.write(rendered_html.encode('utf-8'))

    def _handle_register(self, postvars):
        logger.debug("Handling registration")
        username = postvars['username'][0]
        password = postvars['password'][0]
        User.create_table()
        User.register(username, password)
        self._flash_message('success', 'Your account has been created!')
        self._set_headers(status=302)
        self.send_header('Location', '/login')
        self.end_headers()

    def _handle_login(self, postvars):
        logger.debug("Handling login")
        username = postvars['username'][0]
        password = postvars['password'][0]
        user_id = User.login(username, password)
        if user_id:
            self.send_response(302)
            self.send_header('Set-Cookie', f'user_id={user_id}')
            self.send_header('Location', '/dashboard')
            self.end_headers()
        else:
            self._flash_message('danger', 'Login failed!')
            self._serve_template('login.html', {'messages': self._get_flashed_messages()})

    def _handle_add_contact(self, postvars):
        logger.debug("Handling add contact")
        user_id = self._get_user_id_from_session()
        if not user_id:
            self._set_headers(status=401)
            self.wfile.write(b'User not logged in!')
            return

        full_name = postvars.get('full_name', [''])[0]
        birth_date = postvars.get('birth_date', [''])[0]
        phone_number = postvars.get('phone_number', [''])[0]
        interests = postvars.get('interests', [''])[0]

        if not full_name:
            self._flash_message('danger', 'Full name is required!')
            self._set_headers(status=302)
            self.send_header('Location', '/add_contact')
            self.end_headers()
            return

        contact_id = Contact.add_contact(user_id, full_name, birth_date, phone_number, interests)

        # Обработка нескольких бесед
        conversation_dates = postvars.get('conversation_date', [])
        last_conversations = postvars.get('last_conversation', [])

        for date, conversation in zip(conversation_dates, last_conversations):
            Contact.add_conversation(contact_id, date, conversation)

        self._flash_message('success', 'Contact added successfully!')
        self._set_headers(status=302)
        self.send_header('Location', '/dashboard')
        self.end_headers()

    def _handle_edit_contact(self, postvars):
        logger.debug("Handling edit contact")
        user_id = self._get_user_id_from_session()
        if not user_id:
            self._set_headers(status=401)
            self.wfile.write(b'User not logged in!')
            return

        contact_id = int(postvars.get('id', [0])[0])
        full_name = postvars.get('full_name', [''])[0]
        birth_date = postvars.get('birth_date', [''])[0]
        phone_number = postvars.get('phone_number', [''])[0]
        interests = postvars.get('interests', [''])[0]

        if not full_name:
            self._flash_message('danger', 'Full name is required!')
            self._set_headers(status=302)
            self.send_header('Location', f'/edit_contact?id={contact_id}')
            self.end_headers()
            return

        Contact.edit_contact(contact_id, full_name, birth_date, phone_number, interests)
        self._flash_message('success', 'Contact updated successfully!')
        self._set_headers(status=302)
        self.send_header('Location', '/dashboard')
        self.end_headers()

    def _handle_delete_contact(self, postvars):
        logger.debug("Handling delete contact")
        user_id = self._get_user_id_from_session()
        if not user_id:
            self._set_headers(status=401)
            self.wfile.write(b'User not logged in!')
            return

        contact_id = int(postvars.get('contact_id', [0])[0])
        Contact.delete_contact(contact_id)
        self._flash_message('success', 'Contact deleted successfully!')
        self._set_headers(status=302)
        self.send_header('Location', '/dashboard')
        self.end_headers()

    def _handle_search(self, postvars):
        logger.debug("Handling search")
        user_id = self._get_user_id_from_session()
        if not user_id:
            self._set_headers(status=401)
            self.wfile.write(b'User not logged in!')
            return

        query = postvars.get('query', [''])[0]
        contacts = Contact.search_contacts(user_id, query)
        context = {
            'user_id': user_id,
            'contacts': contacts,
            'messages': self._get_flashed_messages()
        }
        template = env.get_template('dashboard.html')
        rendered_html = template.render(context)
        self._set_headers()
        self.wfile.write(rendered_html.encode('utf-8'))

    def _get_user_id_from_session(self):
        cookies = self.headers.get('Cookie')
        if cookies:
            for cookie in cookies.split('; '):
                key, value = cookie.split('=')
                if key == 'user_id':
                    return int(value)
        return None

    def _flash_message(self, category, message):
        flash_file = os.path.join(os.path.dirname(__file__), 'flash_messages.json')
        try:
            with open(flash_file, 'r') as file:
                flash_messages = json.load(file)
        except FileNotFoundError:
            flash_messages = []

        flash_messages.append({'category': category, 'message': message})
        with open(flash_file, 'w') as file:
            json.dump(flash_messages, file)

    def _get_flashed_messages(self):
        flash_file = os.path.join(os.path.dirname(__file__), 'flash_messages.json')
        try:
            with open(flash_file, 'r') as file:
                flash_messages = json.load(file)
            # Очищаем файл после чтения
            with open(flash_file, 'w') as file:
                json.dump([], file)
            return flash_messages
        except FileNotFoundError:
            return []

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f'Starting httpd server on port {port}...')
    logger.debug(f"Current working directory: {os.getcwd()}")

    # Создание таблиц при старте сервера
    logger.debug("Creating tables at startup...")
    User.create_table()
    Contact.create_table()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down the server.")
        httpd.server_close()

if __name__ == "__main__":
    run()