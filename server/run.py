from app import create_app
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# On Render (or any hosted env with PORT set), serve frontend from project root
_frontend_root = None
if os.getenv('RENDER') or (os.getenv('PORT') and os.getenv('FLASK_ENV', 'development') == 'production'):
    _frontend_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

app = create_app(frontend_root=_frontend_root)

if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 10000)))
    app.run(debug=False, port=port, host='0.0.0.0')
