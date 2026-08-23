from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QThread, Signal

from oauth_flow import GoogleLoginWorker


class LoginScreen(QWidget):

    login_successful = Signal(str, str)
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Posture Tracker"))

        self.login_button = QPushButton("Sign in with Google")
        self.login_button.clicked.connect(self.start_login)
        layout.addWidget(self.login_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.thread = None
        self.worker = None

    def start_login(self):
        self.login_button.setEnabled(False)
        self.status_label.setText("Waiting for Google sign-in in your browser...")

        self.thread = QThread()
        self.worker = GoogleLoginWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_login_success)
        self.worker.failure.connect(self.on_login_failure)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def on_login_success(self, access_token, refresh_token):
        self.status_label.setText("Login successful!")
        self.login_successful.emit(access_token, refresh_token)

    def on_login_failure(self, error_message):
        self.status_label.setText(f"Login failed: {error_message}")
        self.login_button.setEnabled(True)