"""
Database layer — supports SQLite (default) and MySQL.

Set DB_TYPE in .env:
  DB_TYPE=sqlite   → auto-creates calogram.db, zero extra config
  DB_TYPE=mysql    → requires MYSQL_HOST, MYSQL_PORT, MYSQL_USER,
                     MYSQL_PASSWORD, MYSQL_DATABASE
"""
import os
from flask import g


# ── Connection factory ────────────────────────────────────────────────────────

def _connect_sqlite(app):
    import sqlite3
    conn = sqlite3.connect(
        app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def _connect_mysql(app):
    try:
        import pymysql
        import pymysql.cursors
    except ImportError:
        raise RuntimeError(
            'pymysql is required for MySQL support. '
            'Run: pip install pymysql'
        )
    cfg = app.config['MYSQL']
    conn = pymysql.connect(
        host=cfg['host'],
        port=cfg['port'],
        user=cfg['user'],
        password=cfg['password'],
        database=cfg['database'],
        charset=cfg.get('charset', 'utf8mb4'),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    return conn


def get_db():
    from flask import current_app
    if 'db' not in g:
        db_type = current_app.config.get('DB_TYPE', 'sqlite')
        if db_type == 'mysql':
            g.db = _connect_mysql(current_app)
            g.db_type = 'mysql'
        else:
            g.db = _connect_sqlite(current_app)
            g.db_type = 'sqlite'
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    g.pop('db_type', None)
    if db is not None:
        db.close()


def query(sql, params=()):
    """
    Unified query helper for use in route handlers.
    Automatically picks correct placeholder style (? vs %s) based on DB_TYPE.
    Returns cursor/sqlite3.Row results via fetchall/fetchone on the cursor.
    Usage:
        cur = query('SELECT * FROM users WHERE id = ?', (uid,))
        row = cur.fetchone()
    """
    db = get_db()
    db_type = g.get('db_type', 'sqlite')
    return db_execute(db, sql, params, db_type)


def query_commit(sql, params=()):
    """Execute a write query and commit."""
    db = get_db()
    db_type = g.get('db_type', 'sqlite')
    cur = db_execute(db, sql, params, db_type)
    db.commit()
    return cur


# ── Unified execute helper (abstracts ? vs %s placeholder) ────────────────────

def db_execute(db, sql, params=(), db_type='sqlite'):
    """Execute SQL with correct placeholder style for the active DB."""
    if db_type == 'mysql':
        sql = sql.replace('?', '%s')
        cursor = db.cursor()
        cursor.execute(sql, params)
        return cursor
    else:
        return db.execute(sql, params)


def db_executemany(db, sql, data, db_type='sqlite'):
    if db_type == 'mysql':
        sql = sql.replace('?', '%s')
        cursor = db.cursor()
        cursor.executemany(sql, data)
        return cursor
    else:
        return db.executemany(sql, data)


def db_executescript(db, script, db_type='sqlite'):
    if db_type == 'mysql':
        cursor = db.cursor()
        for stmt in script.split(';'):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)
    else:
        db.executescript(script)


# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA_SQLITE = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT DEFAULT '',
        avatar TEXT DEFAULT '',
        age INTEGER,
        weight REAL,
        height REAL,
        gender TEXT,
        goal TEXT DEFAULT 'maintain',
        calorie_goal INTEGER DEFAULT 2000,
        protein_goal INTEGER DEFAULT 120,
        carbs_goal INTEGER DEFAULT 250,
        fat_goal INTEGER DEFAULT 65,
        onboarding_done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        calories REAL NOT NULL,
        protein REAL DEFAULT 0,
        carbs REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        fiber REAL DEFAULT 0,
        sugar REAL DEFAULT 0,
        water REAL DEFAULT 0,
        unit TEXT DEFAULT 'г',
        unit_weight REAL DEFAULT 100,
        nutrition_basis TEXT DEFAULT 'serving',
        default_qty REAL DEFAULT 100,
        is_custom INTEGER DEFAULT 0,
        created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS food_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        food_id INTEGER NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
        quantity REAL NOT NULL DEFAULT 100,
        meal_type TEXT DEFAULT 'breakfast',
        date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, date);
    CREATE INDEX IF NOT EXISTS idx_foods_custom ON foods(is_custom, created_by);

    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        emoji TEXT DEFAULT '🏃',
        calories_burned REAL NOT NULL DEFAULT 0,
        duration_min INTEGER DEFAULT 0,
        activity_type TEXT DEFAULT 'custom',
        date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_activity_logs_user_date ON activity_logs(user_id, date);
'''

_SCHEMA_MYSQL = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255) DEFAULT '',
        avatar VARCHAR(255) DEFAULT '',
        age INT,
        weight FLOAT,
        height FLOAT,
        gender VARCHAR(20),
        goal VARCHAR(20) DEFAULT 'maintain',
        calorie_goal INT DEFAULT 2000,
        protein_goal INT DEFAULT 120,
        carbs_goal INT DEFAULT 250,
        fat_goal INT DEFAULT 65,
        onboarding_done TINYINT(1) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS foods (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        calories FLOAT NOT NULL,
        protein FLOAT DEFAULT 0,
        carbs FLOAT DEFAULT 0,
        fat FLOAT DEFAULT 0,
        fiber FLOAT DEFAULT 0,
        sugar FLOAT DEFAULT 0,
        water FLOAT DEFAULT 0,
        unit VARCHAR(20) DEFAULT 'г',
        unit_weight FLOAT DEFAULT 100,
        nutrition_basis VARCHAR(20) DEFAULT 'serving',
        default_qty FLOAT DEFAULT 100,
        is_custom TINYINT(1) DEFAULT 0,
        created_by INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS food_logs (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        food_id INT NOT NULL,
        quantity FLOAT NOT NULL DEFAULT 100,
        meal_type VARCHAR(20) DEFAULT 'breakfast',
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, date);
    CREATE INDEX IF NOT EXISTS idx_foods_custom ON foods(is_custom, created_by);

    CREATE TABLE IF NOT EXISTS activity_logs (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        emoji VARCHAR(20) DEFAULT '🏃',
        calories_burned FLOAT NOT NULL DEFAULT 0,
        duration_min INT DEFAULT 0,
        activity_type VARCHAR(50) DEFAULT 'custom',
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_activity_logs_user_date ON activity_logs(user_id, date);
'''

# Format: (name, calories, protein, carbs, fat, fiber, sugar, water, unit, unit_weight)
_SEED_FOODS = [
    # ── М'ясо та птиця ───────────────────────────────────────────────────────
    ('Куряча грудка (варена)',    165, 31.0,  0.0,  3.6,  0.0,  0.0, 65.0, 'г',  100),
    ('Куряче стегно (варене)',    215, 26.0,  0.0, 12.0,  0.0,  0.0, 60.0, 'г',  100),
    ('Яловичина нежирна',        218, 26.1,  0.0, 12.1,  0.0,  0.0, 60.0, 'г',  100),
    ('Свинина нежирна',          242, 27.0,  0.0, 14.6,  0.0,  0.0, 57.0, 'г',  100),
    ('Індичка (грудка)',         189, 29.0,  0.0,  7.4,  0.0,  0.0, 63.0, 'г',  100),
    ('Куряча печінка',           136, 20.4,  0.7,  5.5,  0.0,  0.0, 72.0, 'г',  100),
    ('Котлета куряча (парова)',  145, 17.0,  5.0,  6.0,  0.3,  0.2, 62.0, 'г',  100),
    # ── Риба та морепродукти ─────────────────────────────────────────────────
    ('Лосось (запечений)',        208, 20.1,  0.0, 13.4,  0.0,  0.0, 64.0, 'г',  100),
    ('Тунець консервований',      96, 21.5,  0.0,  1.0,  0.0,  0.0, 76.0, 'г',  100),
    ('Тріска варена',             82, 18.0,  0.0,  0.7,  0.0,  0.0, 79.0, 'г',  100),
    ('Скумбрія варена',          211, 18.9,  0.0, 14.4,  0.0,  0.0, 66.0, 'г',  100),
    ('Сьомга слабосолена',       203, 22.5,  0.0, 12.5,  0.0,  0.0, 63.0, 'г',  100),
    ('Оселедець солоний',        215, 14.4,  0.0, 17.5,  0.0,  0.0, 66.0, 'г',  100),
    ('Креветки варені',           99, 20.9,  0.0,  1.1,  0.0,  0.0, 77.0, 'г',  100),
    # ── Яйця та молочні продукти ─────────────────────────────────────────────
    ('Яйце куряче',              155, 12.6,  1.1, 11.3,  0.0,  0.6, 74.0, 'шт',  60),
    ('Білок яячний (сирий)',      52, 10.9,  0.7,  0.2,  0.0,  0.6, 87.0, 'шт',  30),
    ('Жовток яячний',            322, 15.9,  3.6, 27.7,  0.0,  0.6, 50.0, 'шт',  18),
    ('Молоко 2.5%',               52,  2.8,  4.7,  2.5,  0.0,  5.0, 89.0, 'мл', 100),
    ('Молоко 1%',                 42,  3.0,  5.0,  1.0,  0.0,  5.0, 90.0, 'мл', 100),
    ('Кефір 1%',                  40,  3.4,  4.7,  1.0,  0.0,  4.8, 90.0, 'мл', 100),
    ('Кефір 2.5%',                53,  3.0,  4.5,  2.5,  0.0,  4.6, 89.0, 'мл', 100),
    ('Сир кисломолочний 5%',     121, 17.0,  3.0,  5.0,  0.0,  2.8, 74.0, 'г',  100),
    ('Сир кисломолочний 0%',      71, 16.5,  1.8,  0.0,  0.0,  1.5, 80.0, 'г',  100),
    ('Йогурт грецький 2%',        73, 10.0,  3.6,  2.0,  0.0,  3.2, 83.0, 'г',  150),
    ('Йогурт натуральний 3.2%',   68,  5.0,  8.1,  3.2,  0.0,  7.5, 83.0, 'г',  150),
    ('Сир твердий (Гауда)',       356, 25.0,  2.2, 27.4,  0.0,  0.0, 42.0, 'г',   30),
    ('Сир твердий (Пармезан)',    431, 38.5,  4.1, 29.7,  0.0,  0.0, 30.0, 'г',   20),
    ('Сир плавлений',             295, 12.1,  7.5, 24.2,  0.0,  4.5, 50.0, 'г',   30),
    ('Сметана 20%',               206,  2.8,  3.7, 20.0,  0.0,  3.5, 72.0, 'г',   30),
    ('Вершки 10%',                118,  2.8,  4.7, 10.0,  0.0,  4.5, 82.0, 'мл', 100),
    ('Масло вершкове',            748,  0.5,  0.8, 82.5,  0.0,  0.1, 16.0, 'г',   10),
    # ── Крупи та злаки ───────────────────────────────────────────────────────
    ('Гречка варена',             132,  4.5, 25.0,  1.5,  2.7,  0.9, 70.0, 'г',  100),
    ('Вівсяна каша на воді',       68,  2.4, 12.0,  1.4,  1.7,  0.0, 84.0, 'г',  100),
    ('Рис варений (білий)',        130,  2.7, 28.0,  0.3,  0.4,  0.0, 68.0, 'г',  100),
    ('Рис варений (бурий)',        111,  2.6, 23.0,  0.9,  1.8,  0.0, 73.0, 'г',  100),
    ('Макарони варені',            158,  5.5, 31.0,  0.9,  1.8,  0.6, 62.0, 'г',  100),
    ('Вівсяна гранола',            471,  8.5, 67.0, 20.0,  5.0, 18.0,  5.0, 'г',   50),
    ('Кукурудзяна каша',           86,  2.4, 17.0,  1.2,  1.8,  0.5, 78.0, 'г',  100),
    ('Перловка варена',            123,  2.8, 25.0,  0.4,  1.9,  0.0, 71.0, 'г',  100),
    ('Пшоняна каша',               90,  2.7, 17.0,  1.3,  0.8,  0.2, 79.0, 'г',  100),
    ('Манна каша на молоці',       98,  3.0, 16.0,  2.5,  0.2,  5.0, 78.0, 'г',  100),
    ('Мюслі без цукру',           366, 10.1, 58.0, 11.0,  8.5, 12.0,  8.0, 'г',   50),
    # ── Хліб та випічка ──────────────────────────────────────────────────────
    ('Хліб чорний',               214,  7.0, 40.0,  1.3,  5.1,  3.0, 37.0, 'г',  100),
    ('Хліб білий',                265,  8.1, 48.0,  3.2,  2.7,  5.0, 37.0, 'г',  100),
    ('Хліб цільнозерновий',       247,  9.0, 41.0,  3.4,  7.0,  4.0, 38.0, 'г',  100),
    ('Хлібці рисові',             382,  7.0, 83.0,  2.0,  2.8,  0.5,  6.0, 'г',   30),
    # ── Бобові ────────────────────────────────────────────────────────────────
    ('Сочевиця варена',           116,  9.0, 20.0,  0.4,  7.9,  1.8, 70.0, 'г',  100),
    ('Квасоля варена',            127,  8.7, 22.8,  0.5,  6.4,  0.3, 67.0, 'г',  100),
    ('Нут варений',               164,  8.9, 27.4,  2.6,  7.6,  4.8, 60.0, 'г',  100),
    ('Горох варений',             118,  8.3, 21.0,  0.4,  8.3,  2.5, 69.0, 'г',  100),
    ('Едамаме варене',            121, 11.9,  8.9,  5.2,  5.2,  2.2, 71.0, 'г',  100),
    # ── Овочі ─────────────────────────────────────────────────────────────────
    ('Картопля варена',            77,  2.0, 17.0,  0.1,  2.0,  0.8, 80.0, 'г',  100),
    ('Картопля запечена',          93,  2.5, 21.0,  0.1,  2.2,  0.5, 75.0, 'г',  100),
    ('Брокколі варена',            35,  2.4,  7.2,  0.4,  3.3,  1.7, 89.0, 'г',  100),
    ('Цвітна капуста варена',      23,  1.8,  4.1,  0.3,  2.3,  1.9, 92.0, 'г',  100),
    ('Огірок свіжий',              15,  0.7,  3.6,  0.1,  0.5,  1.7, 95.0, 'шт', 150),
    ('Помідор свіжий',             18,  0.9,  3.9,  0.2,  1.2,  2.6, 94.0, 'шт', 130),
    ('Перець болгарський червоний', 31, 1.0,  6.0,  0.3,  2.1,  4.2, 92.0, 'шт', 160),
    ('Перець болгарський зелений',  20, 0.9,  4.6,  0.2,  1.7,  2.4, 93.0, 'шт', 160),
    ('Морква свіжа',               41,  0.9,  9.6,  0.2,  2.8,  4.7, 88.0, 'г',  100),
    ('Морква варена',              35,  0.8,  8.2,  0.2,  3.0,  4.5, 90.0, 'г',  100),
    ('Буряк варений',              49,  1.7, 11.0,  0.2,  2.0,  9.0, 87.0, 'г',  100),
    ('Шпинат свіжий',              23,  2.9,  3.6,  0.4,  2.2,  0.4, 92.0, 'г',  100),
    ('Капуста білокачанна',        27,  1.8,  6.1,  0.1,  2.5,  3.2, 92.0, 'г',  100),
    ('Цукіні/кабачок',             17,  1.2,  3.1,  0.3,  1.0,  2.5, 94.0, 'г',  100),
    ('Гарбуз варений',             20,  0.7,  4.9,  0.1,  0.5,  2.8, 94.0, 'г',  100),
    ('Гриби шампіньони',           27,  2.5,  5.3,  0.3,  1.8,  2.0, 91.0, 'г',  100),
    ('Баклажан запечений',         35,  0.8,  8.7,  0.2,  2.5,  3.5, 90.0, 'г',  100),
    ('Авокадо',                   160,  2.0,  8.5, 14.7,  6.7,  0.7, 73.0, 'шт', 200),
    # ── Фрукти та ягоди ───────────────────────────────────────────────────────
    ('Банан',                      89,  1.1, 23.0,  0.3,  2.6, 12.2, 75.0, 'шт', 120),
    ('Яблуко',                     52,  0.3, 14.0,  0.2,  2.4, 10.4, 86.0, 'шт', 180),
    ('Апельсин',                   47,  0.9, 11.8,  0.1,  2.4,  9.4, 86.0, 'шт', 200),
    ('Грейпфрут',                  42,  0.8, 10.7,  0.1,  1.6,  6.9, 88.0, 'шт', 250),
    ('Полуниця',                   32,  0.7,  7.7,  0.3,  2.0,  4.9, 91.0, 'г',  100),
    ('Чорниця',                    57,  0.7, 14.5,  0.3,  2.4,  9.9, 84.0, 'г',  100),
    ('Малина',                     52,  1.2, 11.9,  0.7,  6.5,  4.4, 86.0, 'г',  100),
    ('Вишня',                      63,  1.1, 16.0,  0.2,  2.1, 13.0, 82.0, 'г',  100),
    ('Мандарин',                   53,  0.8, 13.3,  0.3,  1.8,  9.5, 85.0, 'шт',  80),
    ('Груша',                      57,  0.4, 15.2,  0.1,  3.1,  9.8, 84.0, 'шт', 170),
    ('Персик',                     39,  0.9,  9.5,  0.3,  1.5,  8.4, 89.0, 'шт', 150),
    ('Ківі',                       61,  1.1, 14.7,  0.5,  3.0,  9.0, 84.0, 'шт',  75),
    ('Динь',                       34,  0.8,  8.2,  0.2,  0.9,  7.9, 90.0, 'г',  100),
    ('Кавун',                      30,  0.6,  7.6,  0.2,  0.4,  6.2, 91.0, 'г',  100),
    ('Слива',                      46,  0.7, 11.4,  0.3,  1.4,  9.9, 87.0, 'шт',  50),
    ('Виноград',                   67,  0.6, 17.2,  0.4,  0.9, 16.3, 81.0, 'г',  100),
    ('Манго',                      60,  0.8, 15.0,  0.4,  1.6, 13.7, 83.0, 'г',  100),
    # ── Горіхи та насіння ─────────────────────────────────────────────────────
    ('Грецькі горіхи',            654, 15.2, 13.7, 65.2,  6.7,  2.6,  4.0, 'г',   30),
    ('Мигдаль',                   579, 21.1, 21.6, 49.9, 12.5,  4.4,  4.0, 'г',   30),
    ('Кешью',                     553, 18.2, 30.2, 43.9,  3.3,  5.9,  5.0, 'г',   30),
    ('Фундук',                    628, 14.9, 16.7, 60.8,  9.7,  4.3,  5.0, 'г',   30),
    ('Насіння гарбуза',            559, 30.2, 10.7, 49.1,  6.0,  1.4,  8.0, 'г',   30),
    ('Насіння соняшника',          584, 20.8, 20.0, 51.5,  8.6,  2.6,  5.0, 'г',   30),
    ('Насіння чіа',               486, 16.5, 42.1, 30.7, 34.4,  0.0,  6.0, 'г',   20),
    ('Льон мелений',              534, 18.3, 28.9, 42.2, 27.3,  1.6,  7.0, 'г',   15),
    ('Арахіс смажений',           585, 23.7, 21.5, 49.7,  8.5,  4.0,  2.0, 'г',   30),
    ('Арахісова паста (без цукру)', 589, 25.1, 20.0, 50.4,  6.0,  5.3,  1.0, 'г',  30),
    # ── Олії та жири ──────────────────────────────────────────────────────────
    ('Олія оливкова',              884,  0.0,  0.0, 100.0,  0.0,  0.0,  0.0, 'г',   10),
    ('Олія соняшникова',           884,  0.0,  0.0, 100.0,  0.0,  0.0,  0.0, 'г',   10),
    # ── Мед та солодке ────────────────────────────────────────────────────────
    ('Мед',                       304,  0.3, 82.4,  0.0,  0.2, 82.1,  17.0, 'г',  20),
    ('Варення (ягідне)',           238,  0.3, 59.0,  0.0,  0.0, 58.0,  40.0, 'г',  20),
    ('Шоколад чорний 70%',        598,  7.8, 45.9, 42.6, 10.9, 24.2,   1.5, 'г',  30),
    ('Шоколад молочний',          535,  7.7, 59.4, 29.7,  1.5, 54.0,   1.0, 'г',  30),
    # ── Напої ─────────────────────────────────────────────────────────────────
    ('Кава чорна (без цукру)',       2,  0.3,  0.0,  0.0,  0.0,  0.0, 99.0, 'мл', 200),
    ('Чай чорний (без цукру)',       1,  0.0,  0.3,  0.0,  0.0,  0.0, 99.0, 'мл', 200),
    ('Сік апельсиновий (свіжий)',   45,  0.7, 10.4,  0.2,  0.2,  8.4, 88.0, 'мл', 200),
    ('Вода',                         0,  0.0,  0.0,  0.0,  0.0,  0.0,100.0, 'мл', 200),
    ('Протеїновий коктейль (вода)', 112, 21.0,  6.0,  1.5,  0.3,  3.0, 70.0, 'мл', 300),
]


def init_db(app):
    db_type = app.config.get('DB_TYPE', 'sqlite')
    with app.app_context():
        if db_type == 'mysql':
            db = _connect_mysql(app)
        else:
            import sqlite3
            db = sqlite3.connect(app.config['DATABASE'])
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')

        schema = _SCHEMA_MYSQL if db_type == 'mysql' else _SCHEMA_SQLITE
        db_executescript(db, schema, db_type)
        ensure_schema_updates(db, db_type)

        # Seed shared foods — upsert by name: insert new, update nutrition for existing
        for food in _SEED_FOODS:
            name, cal, prot, carbs, fat, fiber, sugar, water, unit, unit_weight = food
            if db_type == 'mysql':
                cursor = db.cursor()
                cursor.execute('SELECT id, fiber, sugar, water FROM foods WHERE name = %s AND is_custom = 0', (name,))
                exists = cursor.fetchone()
            else:
                exists = db.execute('SELECT id, fiber, sugar, water FROM foods WHERE name = ? AND is_custom = 0', (name,)).fetchone()
            if not exists:
                row = (name, cal, prot, carbs, fat, fiber, sugar, water, unit, unit_weight, unit_weight)
                db_execute(
                    db,
                    'INSERT INTO foods (name, calories, protein, carbs, fat, fiber, sugar, water, unit, unit_weight, nutrition_basis, default_qty, is_custom) '
                    "VALUES (?,?,?,?,?,?,?,?,?,?,'serving',?,0)",
                    row,
                    db_type
                )
            else:
                # Update nutrition data for existing seed foods
                food_id = exists['id'] if db_type == 'mysql' else exists[0]
                db_execute(
                    db,
                    'UPDATE foods SET calories=?, protein=?, carbs=?, fat=?, fiber=?, sugar=?, water=? WHERE id=?',
                    (cal, prot, carbs, fat, fiber, sugar, water, food_id),
                    db_type
                )

        db.commit()
        db.close()
        app.teardown_appcontext(close_db)


def ensure_schema_updates(db, db_type):
    if db_type == 'mysql':
        cursor = db.cursor()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'avatar'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255) DEFAULT ''")
        for col in ('fiber', 'sugar', 'water'):
            cursor.execute(f"SHOW COLUMNS FROM foods LIKE '{col}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE foods ADD COLUMN {col} FLOAT DEFAULT 0")
        cursor.execute("SHOW COLUMNS FROM foods LIKE 'nutrition_basis'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE foods ADD COLUMN nutrition_basis VARCHAR(20) DEFAULT 'serving'")
        cursor.execute("SHOW COLUMNS FROM foods LIKE 'default_qty'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE foods ADD COLUMN default_qty FLOAT DEFAULT 100")
        cursor.execute("SHOW TABLES LIKE 'activity_logs'")
        if not cursor.fetchone():
            cursor.execute("""CREATE TABLE activity_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                emoji VARCHAR(20) DEFAULT '🏃',
                calories_burned FLOAT NOT NULL DEFAULT 0,
                duration_min INT DEFAULT 0,
                activity_type VARCHAR(50) DEFAULT 'custom',
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""")
    else:
        columns = [row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()]
        if 'avatar' not in columns:
            db.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT ''")
        food_columns = [row[1] for row in db.execute("PRAGMA table_info(foods)").fetchall()]
        for col in ('fiber', 'sugar', 'water'):
            if col not in food_columns:
                db.execute(f"ALTER TABLE foods ADD COLUMN {col} REAL DEFAULT 0")
        if 'nutrition_basis' not in food_columns:
            db.execute("ALTER TABLE foods ADD COLUMN nutrition_basis TEXT DEFAULT 'serving'")
        if 'default_qty' not in food_columns:
            db.execute("ALTER TABLE foods ADD COLUMN default_qty REAL DEFAULT 100")
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if 'activity_logs' not in tables:
            db.execute("""CREATE TABLE activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '🏃',
                calories_burned REAL NOT NULL DEFAULT 0,
                duration_min INTEGER DEFAULT 0,
                activity_type TEXT DEFAULT 'custom',
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
