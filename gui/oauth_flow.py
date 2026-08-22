import secrets
import hashlib
import base64
import webbrowser
import requests as http_requests
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from PySide6.QtCore import QObject, Signal
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8765"
DJANGO_AUTH_URL = "http://localhost:8000/api/auth/google/"

print(GOOGLE_CLIENT_ID)

def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge


class _CallbackHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        _CallbackHandler.auth_code = query.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login complete, you can close this tab.")

    def log_message(self, format, *args):
        pass 


def wait_for_auth_code():
    server = HTTPServer(('localhost', 8765), _CallbackHandler)
    server.handle_request()
    return _CallbackHandler.auth_code

class GoogleLoginWorker(QObject):
    success = Signal(str, str)   # access_token, refresh_token
    failure = Signal(str)        # error message
    finished = Signal()          # always emitted when the worker is done

    def run(self):
        try:
            code_verifier, code_challenge = generate_pkce_pair()

            auth_params = {
                'client_id': GOOGLE_CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code',
                'scope': 'openid email',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
            }
            auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(auth_params)
            webbrowser.open(auth_url)

            auth_code = wait_for_auth_code()
            if not auth_code:
                self.failure.emit("No authorization code received.")
                return

            token_response = http_requests.post('https://oauth2.googleapis.com/token', data={
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': auth_code,
                'code_verifier': code_verifier,
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI,
            })

            token_response.raise_for_status()
            id_token_str = token_response.json()['id_token']

            django_response = http_requests.post(DJANGO_AUTH_URL, json={'id_token': id_token_str})
            django_response.raise_for_status()

            tokens = django_response.json()

            self.success.emit(tokens['access'], tokens['refresh'])

        except Exception as e:
            self.failure.emit(str(e))
        finally:
            self.finished.emit()