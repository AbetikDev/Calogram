from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt
import datetime
import re

from ..database import query, query_commit

auth_bp = Blueprint('auth', __name__)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def make_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'Введіть коректний email'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Пароль має бути не менше 6 символів'}), 400

    if query('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
        return jsonify({'error': 'Цей email вже зареєстрований'}), 409

    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor = query_commit(
        'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
        (email, pw_hash, name)
    )
    token = make_token(cursor.lastrowid)
    return jsonify({'token': token, 'onboarding_done': False}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Введіть email і пароль'}), 400

    user = query('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Невірний email або пароль'}), 401

    token = make_token(user['id'])
    return jsonify({
        'token': token,
        'onboarding_done': bool(user['onboarding_done'])
    }), 200
