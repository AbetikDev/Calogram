import os
from server.app import create_app

app = create_app(frontend_root=os.path.dirname(os.path.abspath(__file__)))
