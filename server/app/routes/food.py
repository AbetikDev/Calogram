from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime

from ..database import query, query_commit

food_bp = Blueprint('food', __name__)


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


def row_to_log(row):
    r = dict(row)
    factor = r['quantity'] / (r['unit_weight'] or 100)
    r['total_calories'] = round(r['calories'] * factor, 1)
    r['total_protein']  = round(r['protein']  * factor, 1)
    r['total_carbs']    = round(r['carbs']    * factor, 1)
    r['total_fat']      = round(r['fat']      * factor, 1)
    return r


# ─── Food catalogue ───────────────────────────────────────────────────────────

@food_bp.route('/list', methods=['GET'])
def list_foods():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    search = request.args.get('q', '').strip()
    if search:
        rows = query(
            'SELECT * FROM foods WHERE (is_custom = 0 OR created_by = ?) AND name LIKE ? ORDER BY is_custom ASC, name ASC',
            (uid, f'%{search}%')
        ).fetchall()
    else:
        rows = query(
            'SELECT * FROM foods WHERE is_custom = 0 OR created_by = ? ORDER BY is_custom ASC, name ASC',
            (uid,)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@food_bp.route('/add', methods=['POST'])
def add_food():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    name        = data.get('name', '').strip()
    calories    = data.get('calories')
    protein     = data.get('protein', 0)
    carbs       = data.get('carbs', 0)
    fat         = data.get('fat', 0)
    unit        = data.get('unit', 'г')
    unit_weight = data.get('unit_weight', 100)

    if not name:
        return jsonify({'error': "Назва обов'язкова"}), 400
    if calories is None:
        return jsonify({'error': "Калорії обов'язкові"}), 400

    try:
        calories    = float(calories)
        protein     = float(protein)
        carbs       = float(carbs)
        fat         = float(fat)
        unit_weight = float(unit_weight)
    except (ValueError, TypeError):
        return jsonify({'error': 'Числові значення некоректні'}), 400

    cursor = query_commit(
        'INSERT INTO foods (name, calories, protein, carbs, fat, unit, unit_weight, is_custom, created_by) '
        'VALUES (?,?,?,?,?,?,?,1,?)',
        (name, calories, protein, carbs, fat, unit, unit_weight, uid)
    )
    food = query('SELECT * FROM foods WHERE id = ?', (cursor.lastrowid,)).fetchone()
    return jsonify(dict(food)), 201


@food_bp.route('/delete/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    food = query('SELECT id FROM foods WHERE id = ? AND created_by = ? AND is_custom = 1', (food_id, uid)).fetchone()
    if not food:
        return jsonify({'error': 'Не знайдено або немає дозволу'}), 404

    query_commit('DELETE FROM foods WHERE id = ?', (food_id,))
    return jsonify({'message': 'Видалено'})


# ─── Food log ─────────────────────────────────────────────────────────────────

@food_bp.route('/log', methods=['GET'])
def get_log():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    date = request.args.get('date', datetime.date.today().isoformat())
    rows = query('''
        SELECT fl.id, fl.food_id, fl.quantity, fl.meal_type, fl.date,
               f.name, f.calories, f.protein, f.carbs, f.fat, f.unit, f.unit_weight
        FROM food_logs fl
        JOIN foods f ON f.id = fl.food_id
        WHERE fl.user_id = ? AND fl.date = ?
        ORDER BY fl.created_at
    ''', (uid, date)).fetchall()
    return jsonify([row_to_log(r) for r in rows])


@food_bp.route('/log', methods=['POST'])
def add_log():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    data      = request.get_json(silent=True) or {}
    food_id   = data.get('food_id')
    quantity  = data.get('quantity', 100)
    meal_type = data.get('meal_type', 'breakfast')
    date      = data.get('date', datetime.date.today().isoformat())

    if not food_id:
        return jsonify({'error': "food_id обов'язковий"}), 400

    food = query(
        'SELECT id FROM foods WHERE id = ? AND (is_custom = 0 OR created_by = ?)',
        (food_id, uid)
    ).fetchone()
    if not food:
        return jsonify({'error': 'Продукт не знайдено'}), 404

    cursor = query_commit(
        'INSERT INTO food_logs (user_id, food_id, quantity, meal_type, date) VALUES (?,?,?,?,?)',
        (uid, food_id, quantity, meal_type, date)
    )
    return jsonify({'id': cursor.lastrowid, 'message': 'Додано'}), 201


@food_bp.route('/log/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    entry = query('SELECT id FROM food_logs WHERE id = ? AND user_id = ?', (log_id, uid)).fetchone()
    if not entry:
        return jsonify({'error': 'Запис не знайдено'}), 404

    query_commit('DELETE FROM food_logs WHERE id = ?', (log_id,))
    return jsonify({'message': 'Видалено'})


# ─── Daily stats ──────────────────────────────────────────────────────────────

@food_bp.route('/stats', methods=['GET'])
def get_stats():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    date = request.args.get('date', datetime.date.today().isoformat())
    rows = query('''
        SELECT fl.quantity, f.calories, f.protein, f.carbs, f.fat, f.unit_weight
        FROM food_logs fl
        JOIN foods f ON f.id = fl.food_id
        WHERE fl.user_id = ? AND fl.date = ?
    ''', (uid, date)).fetchall()

    totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
    for row in rows:
        factor = row['quantity'] / (row['unit_weight'] or 100)
        totals['calories'] += row['calories'] * factor
        totals['protein']  += row['protein']  * factor
        totals['carbs']    += row['carbs']    * factor
        totals['fat']      += row['fat']      * factor

    totals = {k: round(v, 1) for k, v in totals.items()}

    user = query(
        'SELECT calorie_goal, protein_goal, carbs_goal, fat_goal FROM users WHERE id = ?', (uid,)
    ).fetchone()
    if user:
        totals.update({
            'calorie_goal': user['calorie_goal'] or 2000,
            'protein_goal': user['protein_goal'] or 120,
            'carbs_goal':   user['carbs_goal']   or 250,
            'fat_goal':     user['fat_goal']      or 65,
        })
    else:
        totals.update({'calorie_goal': 2000, 'protein_goal': 120, 'carbs_goal': 250, 'fat_goal': 65})

    return jsonify(totals)


# ─── Weekly stats ─────────────────────────────────────────────────────────────

@food_bp.route('/stats/week', methods=['GET'])
def get_week_stats():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    today = datetime.date.today()
    days  = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    result = []
    for day in days:
        rows = query('''
            SELECT fl.quantity, f.calories, f.unit_weight
            FROM food_logs fl JOIN foods f ON f.id = fl.food_id
            WHERE fl.user_id = ? AND fl.date = ?
        ''', (uid, day)).fetchall()
        total = sum(r['calories'] * r['quantity'] / (r['unit_weight'] or 100) for r in rows)
        result.append({'date': day, 'calories': round(total, 1)})

    return jsonify(result)
