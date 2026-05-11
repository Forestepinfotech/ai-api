"""
Plesk Passenger entry point.
Passenger expects a WSGI 'application' callable.
a2wsgi wraps our ASGI FastAPI app so Passenger can serve it.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware
from main import app

application = ASGIMiddleware(app)
