from flask import Blueprint, request, jsonify, current_app
import jwt

from ..database import query, query_commit

user_bp = Blueprint('user', __name__)


def get_user_id():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def estimate_height(age, gender):
    age = age or 25
    if gender == 'female':
        if age < 18:
            return 162
        return 166
    if gender == 'male':
        if age < 18:
            return 173
        return 178
    return 172


def calc_goals(age, weight, height, gender, goal):
    h = float(height or estimate_height(age, gender))
    w = float(weight or 70)
    a = int(age or 25)
    g = (gender or 'other').lower()
    target = (goal or 'maintain').lower()

    if g == 'female':
        bmr = 10 * w + 6.25 * h - 5 * a - 161
    else:
        bmr = 10 * w + 6.25 * h - 5 * a + 5

    activity_factor = 1.45 if a < 18 else 1.5
    tdee = bmr * activity_factor

    if target == 'lose':
        calories = max(1400, int(tdee - max(280, w * 4.2)))
        protein_ratio = 2.0
        fat_ratio = 0.27
    elif target == 'gain':
        calories = int(tdee + max(240, w * 3.6))
        protein_ratio = 1.85
        fat_ratio = 0.24
    else:
        calories = int(tdee)
        protein_ratio = 1.75
        fat_ratio = 0.25

    protein = max(90, int(round(w * protein_ratio)))
    fat = max(45, int(round((calories * fat_ratio) / 9)))
    carbs = max(90, int(round((calories - protein * 4 - fat * 9) / 4)))
    return calories, protein, carbs, fat


@user_bp.route('/me', methods=['GET'])
def me():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    user = query(
        'SELECT id, email, name, avatar, age, weight, height, gender, goal, '
        'calorie_goal, protein_goal, carbs_goal, fat_goal, onboarding_done '
        'FROM users WHERE id = ?', (uid,)
    ).fetchone()
    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(user))


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    allowed = ['name', 'avatar', 'age', 'weight', 'height', 'gender', 'goal',
               'calorie_goal', 'protein_goal', 'carbs_goal', 'fat_goal', 'onboarding_done']
    updates = {k: data[k] for k in allowed if k in data}

    if not updates:
        return jsonify({'error': 'Нічого для оновлення'}), 400

    body_fields = {'age', 'weight', 'height', 'gender', 'goal'}
    if body_fields & set(updates.keys()):
        user = query('SELECT * FROM users WHERE id = ?', (uid,)).fetchone()
        age    = updates.get('age',    user['age'])
        weight = updates.get('weight', user['weight'])
        height = updates.get('height', user['height'])
        gender = updates.get('gender', user['gender'])
        goal   = updates.get('goal',   user['goal'])

        calories, protein, carbs, fat = calc_goals(age, weight, height, gender, goal)
        if 'calorie_goal' not in updates: updates['calorie_goal'] = calories
        if 'protein_goal' not in updates: updates['protein_goal'] = protein
        if 'carbs_goal'   not in updates: updates['carbs_goal']   = carbs
        if 'fat_goal'     not in updates: updates['fat_goal']     = fat

    set_clause = ', '.join(f'{k} = ?' for k in updates)
    values = list(updates.values()) + [uid]
    query_commit(f'UPDATE users SET {set_clause} WHERE id = ?', values)

    user = query(
        'SELECT id, email, name, avatar, age, weight, height, gender, goal, '
        'calorie_goal, protein_goal, carbs_goal, fat_goal, onboarding_done '
        'FROM users WHERE id = ?', (uid,)
    ).fetchone()
    return jsonify(dict(user))
