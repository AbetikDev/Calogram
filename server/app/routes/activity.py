from flask import Blueprint, request, jsonify, current_app
import jwt

from ..database import query, query_commit

activity_bp = Blueprint('activity', __name__)

PRESET_ACTIVITIES = [
    {'id': 'walking',    'name': 'Ходьба',           'kcal_per_min': 4,  'emoji': '🚶'},
    {'id': 'running',    'name': 'Біг',               'kcal_per_min': 10, 'emoji': '🏃'},
    {'id': 'cycling',    'name': 'Велосипед',          'kcal_per_min': 8,  'emoji': '🚴'},
    {'id': 'swimming',   'name': 'Плавання',           'kcal_per_min': 8,  'emoji': '🏊'},
    {'id': 'gym',        'name': 'Тренажерний зал',    'kcal_per_min': 6,  'emoji': '🏋️'},
    {'id': 'yoga',       'name': 'Йога',               'kcal_per_min': 3,  'emoji': '🧘'},
    {'id': 'dancing',    'name': 'Танці',              'kcal_per_min': 5,  'emoji': '💃'},
    {'id': 'football',   'name': 'Футбол',             'kcal_per_min': 9,  'emoji': '⚽'},
    {'id': 'hiit',       'name': 'HIIT',               'kcal_per_min': 12, 'emoji': '🔥'},
    {'id': 'stretching', 'name': 'Розтяжка',           'kcal_per_min': 2,  'emoji': '🤸'},
    {'id': 'basketball', 'name': 'Баскетбол',          'kcal_per_min': 8,  'emoji': '🏀'},
    {'id': 'boxing',     'name': 'Бокс',               'kcal_per_min': 11, 'emoji': '🥊'},
]


def get_user_id():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        return payload.get('user_id')
    except Exception:
        return None


@activity_bp.route('/presets', methods=['GET'])
def get_presets():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(PRESET_ACTIVITIES)


@activity_bp.route('/log', methods=['GET'])
def get_log():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    date = request.args.get('date', '')
    if not date:
        return jsonify([])
    cur = query(
        'SELECT * FROM activity_logs WHERE user_id = ? AND date = ? ORDER BY created_at ASC',
        (user_id, date)
    )
    rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


@activity_bp.route('/log', methods=['POST'])
def add_log():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    date = (data.get('date') or '').strip()
    if not name or not date:
        return jsonify({'error': 'name and date are required'}), 400
    calories_burned = float(data.get('calories_burned') or 0)
    duration_min = int(data.get('duration_min') or 0)
    activity_type = (data.get('activity_type') or 'custom').strip()
    emoji = (data.get('emoji') or '🏃').strip()

    cur = query_commit(
        'INSERT INTO activity_logs (user_id, name, emoji, calories_burned, duration_min, activity_type, date) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, name, emoji, calories_burned, duration_min, activity_type, date)
    )
    row_id = cur.lastrowid
    row = query('SELECT * FROM activity_logs WHERE id = ?', (row_id,)).fetchone()
    return jsonify(dict(row)), 201


@activity_bp.route('/log/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    query_commit(
        'DELETE FROM activity_logs WHERE id = ? AND user_id = ?',
        (log_id, user_id)
    )
    return jsonify({'ok': True})
