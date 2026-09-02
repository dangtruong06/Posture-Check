import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel
from login_screen import LoginScreen
from dashboard_screen import DashboardScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posture Tracker")
        self.resize(800, 600)

        self.access_token = None
        self.refresh_token = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_screen = LoginScreen()
        self.dashboard_screen = DashboardScreen()

        self.login_screen.login_successful.connect(self.on_login_successful)

        self.stack.addWidget(self.login_screen)      # index 0
        self.stack.addWidget(self.dashboard_screen)   # index 1 

        self.stack.setCurrentIndex(0)  # start on login

    def on_login_successful(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.dashboard_screen.load_data(access_token)  # STILL NEED TO WRITE THIS FUNCTION
        self.stack.setCurrentIndex(1)

        self.raise_()
        self.activateWindow()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()