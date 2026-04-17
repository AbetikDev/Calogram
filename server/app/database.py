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
'''

_SEED_FOODS = [
    ('Куряча грудка (варена)', 165, 31.0, 0.0, 3.6, 'г', 100),
    ('Яйце куряче', 155, 12.6, 1.1, 11.3, 'шт', 60),
    ('Гречка варена', 132, 4.5, 25.0, 1.5, 'г', 100),
    ('Вівсяна каша на воді', 68, 2.4, 12.0, 1.4, 'г', 100),
    ('Рис варений', 130, 2.7, 28.0, 0.3, 'г', 100),
    ('Молоко 2.5%', 52, 2.8, 4.7, 2.5, 'мл', 100),
    ('Банан', 89, 1.1, 23.0, 0.3, 'шт', 120),
    ('Яблуко', 52, 0.3, 14.0, 0.2, 'шт', 180),
    ('Хліб чорний', 214, 7.0, 40.0, 1.3, 'г', 100),
    ('Сир кисломолочний 5%', 121, 17.0, 3.0, 5.0, 'г', 100),
    ('Лосось', 208, 20.1, 0.0, 13.4, 'г', 100),
    ('Картопля варена', 77, 2.0, 17.0, 0.1, 'г', 100),
    ('Огірок свіжий', 15, 0.7, 3.6, 0.1, 'шт', 150),
    ('Помідор свіжий', 18, 0.9, 3.9, 0.2, 'шт', 130),
    ('Кефір 1%', 40, 3.4, 4.7, 1.0, 'мл', 100),
    ('Грецькі горіхи', 654, 15.2, 13.7, 65.2, 'г', 30),
    ('Мед', 304, 0.3, 82.4, 0.0, 'г', 20),
    ('Масло вершкове', 748, 0.5, 0.8, 82.5, 'г', 10),
    ('Сир твердий', 402, 25.0, 0.1, 33.0, 'г', 30),
    ('Макарони варені', 158, 5.5, 31.0, 0.9, 'г', 100),
    ('Тунець консервований', 96, 21.5, 0.0, 1.0, 'г', 100),
    ('Авокадо', 160, 2.0, 8.5, 14.7, 'шт', 200),
    ('Грейпфрут', 42, 0.8, 10.7, 0.1, 'шт', 250),
    ('Мигдаль', 579, 21.1, 21.6, 49.9, 'г', 30),
    ('Йогурт грецький 2%', 73, 10.0, 3.6, 2.0, 'г', 150),
    ('Вівсяна гранола', 471, 8.5, 67.0, 20.0, 'г', 50),
    ('Шоколад чорний 70%', 598, 7.8, 45.9, 42.6, 'г', 30),
    ('Апельсин', 47, 0.9, 11.8, 0.1, 'шт', 200),
    ('Полуниця', 32, 0.7, 7.7, 0.3, 'г', 100),
    ('Брокколі варена', 35, 2.4, 7.2, 0.4, 'г', 100),
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

        # Seed shared foods
        if db_type == 'mysql':
            cursor = db.cursor()
            cursor.execute('SELECT COUNT(*) as cnt FROM foods WHERE is_custom = 0')
            existing = cursor.fetchone()['cnt']
        else:
            existing = db.execute('SELECT COUNT(*) FROM foods WHERE is_custom = 0').fetchone()[0]

        if existing == 0:
            seed_foods = [(*food, food[-1]) for food in _SEED_FOODS]
            db_executemany(
                db,
                'INSERT INTO foods (name, calories, protein, carbs, fat, unit, unit_weight, nutrition_basis, default_qty, is_custom) '
                "VALUES (?,?,?,?,?,?,?,'serving',?,0)",
                seed_foods,
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
