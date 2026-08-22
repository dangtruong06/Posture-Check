from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dashboard"))

        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)