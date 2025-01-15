import argparse
from models import User, Contact
from bcrypt import gensalt, hashpw, checkpw
from getpass import getpass

def register_user(username, password):
    password_hash = hashpw(password.encode('utf-8'), gensalt())
    User.create_table()
    User.register(username, password_hash.decode('utf-8'))
    print("User registered successfully!")

def login_user(username, password):
    result = User.login(username)
    if result and checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
        print(f"Logged in as {result[1]}")
        return result[0]  # Return user_id
    else:
        print("Login failed!")
        return None

def add_contact(user_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date):
    Contact.create_table()
    Contact.add_contact(user_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date)
    print("Contact added successfully!")

def list_contacts(user_id):
    contacts = Contact.get_contacts(user_id)
    for contact in contacts:
        print(f"ID: {contact[0]}, Name: {contact[3]}, Phone: {contact[4]}, Interests: {contact[5]}")

def edit_contact(contact_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date):
    Contact.edit_contact(contact_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date)
    print("Contact updated successfully!")

def delete_contact(contact_id):
    Contact.delete_contact(contact_id)
    print("Contact deleted successfully!")

def search_contacts(user_id, query):
    results = Contact.search_contacts(user_id, query)
    for contact in results:
        print(f"ID: {contact[0]}, Name: {contact[3]}, Phone: {contact[4]}, Interests: {contact[5]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Networking Service CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new user')
    register_parser.add_argument('username', type=str, help='Username')
    register_parser.add_argument('--password', type=str, help='Password')

    # Login command
    login_parser = subparsers.add_parser('login', help='Log in a user')
    login_parser.add_argument('username', type=str, help='Username')
    login_parser.add_argument('--password', type=str, help='Password')

    # Add contact command
    add_contact_parser = subparsers.add_parser('add_contact', help='Add a new contact')
    add_contact_parser.add_argument('user_id', type=int, help='User ID')
    add_contact_parser.add_argument('full_name', type=str, help='Full name')
    add_contact_parser.add_argument('birth_date', type=str, help='Birth date (YYYY-MM-DD)')
    add_contact_parser.add_argument('phone_number', type=str, help='Phone number')
    add_contact_parser.add_argument('interests', type=str, help='Interests')
    add_contact_parser.add_argument('last_conversation', type=str, help='Last conversation')
    add_contact_parser.add_argument('conversation_date', type=str, help='Conversation date (YYYY-MM-DD)')

    # List contacts command
    list_contacts_parser = subparsers.add_parser('list_contacts', help='List all contacts')
    list_contacts_parser.add_argument('user_id', type=int, help='User ID')

    # Edit contact command
    edit_contact_parser = subparsers.add_parser('edit_contact', help='Edit an existing contact')
    edit_contact_parser.add_argument('contact_id', type=int, help='Contact ID')
    edit_contact_parser.add_argument('full_name', type=str, help='Full name')
    edit_contact_parser.add_argument('birth_date', type=str, help='Birth date (YYYY-MM-DD)')
    edit_contact_parser.add_argument('phone_number', type=str, help='Phone number')
    edit_contact_parser.add_argument('interests', type=str, help='Interests')
    edit_contact_parser.add_argument('last_conversation', type=str, help='Last conversation')
    edit_contact_parser.add_argument('conversation_date', type=str, help='Conversation date (YYYY-MM-DD)')

    # Delete contact command
    delete_contact_parser = subparsers.add_parser('delete_contact', help='Delete a contact')
    delete_contact_parser.add_argument('contact_id', type=int, help='Contact ID')

    # Search contacts command
    search_contacts_parser = subparsers.add_parser('search_contacts', help='Search contacts by query')
    search_contacts_parser.add_argument('user_id', type=int, help='User ID')
    search_contacts_parser.add_argument('query', type=str, help='Search query')

    args = parser.parse_args()

    if args.command == 'register':
        password = getpass('Enter password: ') if not args.password else args.password
        register_user(args.username, password)

    elif args.command == 'login':
        password = getpass('Enter password: ') if not args.password else args.password
        user_id = login_user(args.username, password)
        if user_id:
            print(f"Logged in user ID: {user_id}")

    elif args.command == 'add_contact':
        add_contact(args.user_id, args.full_name, args.birth_date, args.phone_number, args.interests, args.last_conversation, args.conversation_date)

    elif args.command == 'list_contacts':
        list_contacts(args.user_id)

    elif args.command == 'edit_contact':
        edit_contact(args.contact_id, args.full_name, args.birth_date, args.phone_number, args.interests, args.last_conversation, args.conversation_date)

    elif args.command == 'delete_contact':
        delete_contact(args.contact_id)

    elif args.command == 'search_contacts':
        search_contacts(args.user_id, args.query)