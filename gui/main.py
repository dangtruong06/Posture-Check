import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel
from login_screen import LoginScreen
from dashboard_screen import DashboardScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posture Tracker")
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # placeholders for now — real screens come next
        self.login_screen = LoginScreen()
        self.dashboard_screen = DashboardScreen()

        self.stack.addWidget(self.login_screen)      # index 0
        self.stack.addWidget(self.dashboard_screen)   # index 1 

        self.stack.setCurrentIndex(0)  # start on login

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()