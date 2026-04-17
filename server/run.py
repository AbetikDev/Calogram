from app import create_app
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 10000)))
    app.run(debug=False, port=port, host='0.0.0.0')
