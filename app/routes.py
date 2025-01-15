from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models import User, Contact
from app import bcrypt, login_manager
from functools import wraps

main = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return user_id

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        User.register(username, hashed_password)
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.login(username)
        if user and bcrypt.check_password_hash(user[2].encode('utf-8'), password.encode('utf-8')):
            session['user_id'] = user[0]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    contacts = Contact.get_contacts(user_id)
    return render_template('dashboard.html', contacts=contacts)

@main.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        user_id = session['user_id']
        full_name = request.form['full_name']
        birth_date = request.form['birth_date']
        phone_number = request.form['phone_number']
        interests = request.form['interests']
        last_conversation = request.form['last_conversation']
        conversation_date = request.form['conversation_date']
        Contact.add_contact(user_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date)
        flash('Contact added successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_contact.html')

@main.route('/edit_contact/<int:contact_id>', methods=['POST'])
@login_required
def edit_contact(contact_id):
    user_id = session['user_id']
    full_name = request.form['full_name']
    birth_date = request.form['birth_date']
    phone_number = request.form['phone_number']
    interests = request.form['interests']
    last_conversation = request.form['last_conversation']
    conversation_date = request.form['conversation_date']
    Contact.edit_contact(contact_id, full_name, birth_date, phone_number, interests, last_conversation, conversation_date)
    flash('Contact updated successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/delete_contact/<int:contact_id>')
@login_required
def delete_contact(contact_id):
    Contact.delete_contact(contact_id)
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/search', methods=['POST'])
@login_required
def search():
    query = request.form['query']
    user_id = session['user_id']
    contacts = Contact.search_contacts(user_id, query)
    return render_template('dashboard.html', contacts=contacts)