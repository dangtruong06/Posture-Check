from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import subprocess
from pathlib import Path
import requests
import os

BASE_DIR = Path(__file__).resolve().parent.parent 
CV_CLIENT_PYTHON = BASE_DIR / "cv_client" / "venv" / "bin" / "python"
CV_CLIENT_MAIN = BASE_DIR / "cv_client" / "main.py"
BACKEND_BASE_URL = 'http://127.0.0.1:8000/'


class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dashboard"))

        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.camera_process = None

    def start_camera(self):
        env = os.environ.copy()
        env["POSTURE_ACCESS_TOKEN"] = self.access_token

        self.camera_process = subprocess.Popen([str(CV_CLIENT_PYTHON), str(CV_CLIENT_MAIN)], env=env)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def stop_camera(self):
        if self.camera_process:
            self.camera_process.terminate()
            self.camera_process = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def load_data(self, access_token):
        self.access_token = access_token
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get('http://127.0.0.1:8000/api/posture_summaries', headers=headers)
        data = response.json()
        print(data)
