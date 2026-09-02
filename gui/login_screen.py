from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import QThread, Signal, Qt, QSize
from PySide6.QtGui import QIcon

from oauth_flow import GoogleLoginWorker

card_width = 400

class LoginScreen(QWidget):

    login_successful = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.setObjectName("LoginScreen")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self._stylesheet())

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(card_width)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(28, 40, 28, 40)
        card_layout.setSpacing(10)
        

        badge = QLabel()
        badge.setObjectName("Badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(52, 52)

        icon = QIcon("assets/laptop.png")
        badge.setPixmap(icon.pixmap(28, 28))

        title = QLabel("Improve your posture")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)

        subtitle = QLabel("View trends, habits, and change")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Log in with Google")
        self.login_button.setObjectName("LoginButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setFixedHeight(44)
        self.login_button.setFixedWidth(int(card_width * 0.6))
        self.login_button.setIcon(QIcon("assets/google.svg"))
        self.login_button.setIconSize(QSize(20, 20))
        self.login_button.clicked.connect(self.start_login)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(False)

        card_layout.addWidget(badge, alignment=Qt.AlignCenter)
        card_layout.addSpacing(8)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(14)
        card_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.status_label)

        card.setLayout(card_layout)
        outer_layout.addWidget(card)
        self.setLayout(outer_layout)

        self.thread = None
        self.worker = None

    def start_login(self):
        self.login_button.setEnabled(False)
        self.login_button.setText("Signing in...")
        self.status_label.setStyleSheet("")
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
        self.login_button.setEnabled(True)
        self.login_button.setText("Log in now")
        self.status_label.setStyleSheet("color: #d9534f;")
        self.status_label.setText(f"Login failed: {error_message}")

    @staticmethod
    def _stylesheet():
        return """
            #LoginScreen {
                background-color: #FAF9F5;
            }
            #Card {
                background-color: #ffffff;
                border-radius: 14px;
                border: 1px solid #ece7dc;
            }
            #Badge {
                background-color: #FAEEDA;
                border-radius: 26px;
                color: #854F0B;
                font-size: 18px;
            }
            #Title {
                font-size: 19px;
                font-weight: 600;
                color: #412402;
            }
            #Subtitle {
                font-size: 13px;
                color: #6b7280;
            }
            #LoginButton {
                background-color: #BA7517;
                color: white;
                font-size: 14px;
                font-weight: 500;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
            }
            #LoginButton:hover {
                background-color: #9c6412;
            }
            #LoginButton:disabled {
                background-color: #e0c193;
                color: #f5f0e6;
            }
            #StatusLabel {
                font-size: 12px;
                color: #6b7280;
                margin-top: 4px;
            }
        """