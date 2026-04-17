from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from .database import init_db
from .routes.auth import auth_bp
from .routes.user import user_bp
from .routes.food import food_bp
from .routes.activity import activity_bp


def create_app(frontend_root=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'jwt-secret-key')

    # ── Database type: sqlite (default) or mysql ──────────────────
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    app.config['DB_TYPE'] = db_type

    if db_type == 'sqlite':
        default_db_path = 'calogram.db'
        if os.getenv('VERCEL'):
            default_db_path = '/tmp/calogram.db'
        app.config['DATABASE'] = os.path.join(
            os.path.dirname(__file__), '..', os.getenv('DATABASE_PATH', default_db_path)
        )
    elif db_type == 'mysql':
        app.config['MYSQL'] = {
            'host':     os.getenv('MYSQL_HOST', 'localhost'),
            'port':     int(os.getenv('MYSQL_PORT', '3306')),
            'user':     os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'calogram_db'),
            'charset':  os.getenv('MYSQL_CHARSET', 'utf8mb4'),
        }
    else:
        raise ValueError(f"Unknown DB_TYPE='{db_type}'. Use 'sqlite' or 'mysql'.")

    # ── Subscription pricing ──────────────────────────────────────
    app.config['SUB_MONTHLY_USD'] = float(os.getenv('SUBSCRIPTION_MONTHLY_USD', '4.99'))
    app.config['SUB_YEARLY_USD']  = float(os.getenv('SUBSCRIPTION_YEARLY_USD', '29.99'))
    app.config['SUB_TRIAL_DAYS']  = int(os.getenv('SUBSCRIPTION_TRIAL_DAYS', '7'))

    # ── CORS ──────────────────────────────────────────────────────
    cors_origins = os.getenv('CORS_ORIGINS', '*').strip()
    if cors_origins == '*':
        CORS(app, origins='*',
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    else:
        origins = [o.strip() for o in cors_origins.split(',')]
        CORS(app, origins=origins, supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(food_bp, url_prefix='/api/food')
    app.register_blueprint(activity_bp, url_prefix='/api/activity')

    @app.route('/api/ping')
    def ping():
        return {'status': 'ok', 'message': 'Calogram API is running', 'db': db_type}

    # ── Serve frontend static files ───────────────────────────────
    if frontend_root:
        @app.route('/')
        def serve_index():
            return send_from_directory(frontend_root, 'index.html')

        @app.route('/home.html')
        def serve_home():
            return send_from_directory(frontend_root, 'home.html')

        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            return send_from_directory(os.path.join(frontend_root, 'assets'), filename)

        @app.route('/<path:path>')
        def serve_catchall(path):
            # Never intercept API routes — let Flask blueprints handle them
            if path.startswith('api/'):
                from flask import abort
                abort(404)
            fp = os.path.join(frontend_root, path)
            if os.path.isfile(fp):
                return send_from_directory(frontend_root, path)
            return send_from_directory(frontend_root, 'index.html')

    @app.route('/api/subscription/plans')
    def subscription_plans():
        return {
            'trial_days': app.config['SUB_TRIAL_DAYS'],
            'plans': [
                {
                    'id': 'monthly',
                    'name': 'Місячна підписка',
                    'price_usd': app.config['SUB_MONTHLY_USD'],
                    'period': 'month',
                    'per_day_usd': round(app.config['SUB_MONTHLY_USD'] / 30, 3),
                },
                {
                    'id': 'yearly',
                    'name': 'Річна підписка',
                    'price_usd': app.config['SUB_YEARLY_USD'],
                    'period': 'year',
                    'per_day_usd': round(app.config['SUB_YEARLY_USD'] / 365, 3),
                    'discount_pct': round(
                        (1 - app.config['SUB_YEARLY_USD'] /
                         (app.config['SUB_MONTHLY_USD'] * 12)) * 100, 1
                    ),
                }
            ]
        }

    return app
