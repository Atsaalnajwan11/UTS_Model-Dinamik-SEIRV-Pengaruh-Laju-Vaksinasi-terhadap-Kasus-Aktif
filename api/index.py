import os
import sys

# Tambahkan direktori root proyek ke path Python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Flask instance dari app.py
from app import app

class VercelPathFixer:
    """
    WSGI Middleware untuk menangani routing di Vercel Serverless Function.
    Memastikan bahwa URL yang di-rewrite ke /api/index dapat dipetakan
    kembali ke route Flask yang benar ('/' atau '/api/simulate').
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = (
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('REQUEST_URI') or
            environ.get('RAW_URI')
        )
        path_info = environ.get('PATH_INFO', '')

        if matched_path:
            clean_path = matched_path.split('?')[0]
            if clean_path and not clean_path.startswith('/api/index'):
                environ['PATH_INFO'] = clean_path
            elif path_info.startswith('/api/index'):
                sub = path_info[len('/api/index'):]
                environ['PATH_INFO'] = sub if sub else '/'
        else:
            if path_info in ('/api/index', '/api/index/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[len('/api/index'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixer(app.wsgi_app)

