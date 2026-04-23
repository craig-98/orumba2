import sys
import os

# Add top-level dir (parent of app/) to Python path so 'app.py' is importable as 'app'
top_level_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if top_level_dir not in sys.path:
    sys.path.insert(0, top_level_dir)

# Fixed circular import - import from top-level app.py\n# from app import app  # DISABLED\n


# Make 'app' available at module level for api/index.py
__all__ = ['app']

