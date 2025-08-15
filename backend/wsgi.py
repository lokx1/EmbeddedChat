import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/EmbeddedChat/backend'
if path not in sys.path:
    sys.path.append(path)

from main import app

# PythonAnywhere expects 'application'
application = app 