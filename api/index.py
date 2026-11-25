import os
import sys

# Tambahkan direktori root proyek ke path Python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Flask instance dari app.py
from app import app
