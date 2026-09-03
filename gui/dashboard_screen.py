from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import QThread, QObject, QTimer, Signal, Qt
import subprocess
from pathlib import Path
import requests
import os

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

BASE_DIR = Path(__file__).resolve().parent.parent
CV_CLIENT_PYTHON = BASE_DIR / "cv_client" / "venv" / "bin" / "python"
CV_CLIENT_MAIN = BASE_DIR / "cv_client" / "main.py"
BACKEND_BASE_URL = 'http://127.0.0.1:8000/'
REFRESH_INTERVAL_MS = 5 * 60 * 1000 + 15 * 1000
# 5 * 60 * 1000 + 15 * 1000
# test value 10 * 1000
GOOD_COLOR = "#31eb53"
BAD_COLOR = "#fa512a"


class SummaryFetchWorker(QObject):

    success = Signal(list)
    failure = Signal(str)
    finished = Signal()

    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token

    def run(self):
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f'{BACKEND_BASE_URL}api/posture_summaries',
                headers=headers,
            )
            response.raise_for_status()
            self.success.emit(response.json())
        except requests.RequestException as e:
            self.failure.emit(str(e))
        finally:
            self.finished.emit()


class StatCard(QFrame):
    def __init__(self, label_text, value_color):
        super().__init__()
        self.setObjectName("StatCard")
        self.value_color = value_color

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setObjectName("StatLabel")

        self.value = QLabel("--")
        self.value.setObjectName("StatValue")
        self.value.setStyleSheet(f"color: {value_color};")

        self.subvalue = QLabel("")
        self.subvalue.setObjectName("StatSubvalue")

        layout.addWidget(self.label)
        layout.addWidget(self.value)
        layout.addWidget(self.subvalue)
        self.setLayout(layout)

    def set_values(self, main_text, sub_text=""):
        self.value.setText(main_text)
        self.subvalue.setText(sub_text)


class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("DashboardScreen")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self._stylesheet())

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Posture tracker")
        title.setObjectName("Title")

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.setObjectName("StartButton")
        self.stop_button.setObjectName("StopButton")
        self.stop_button.setEnabled(False)
        self.start_button.setFixedHeight(28)
        self.stop_button.setFixedHeight(28)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.start_button)
        header.addWidget(self.stop_button)

        content = QFrame()
        content.setObjectName("ContentCard")
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # Left side: pie chart + legend
        chart_card = QFrame()
        chart_card.setObjectName("ChartCard")
        chart_layout = QVBoxLayout()
        chart_layout.setAlignment(Qt.AlignCenter)

        self.figure = Figure(figsize=(2.2, 2.2))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        self.figure.patch.set_alpha(0)

        legend = QHBoxLayout()
        legend.setAlignment(Qt.AlignCenter)
        legend.setSpacing(16)
        legend.addWidget(self._legend_item("Good", GOOD_COLOR))
        legend.addWidget(self._legend_item("Bad", BAD_COLOR))

        chart_layout.addWidget(self.canvas)
        chart_layout.addLayout(legend)
        chart_card.setLayout(chart_layout)

        # Right side: stat cards
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)

        self.good_card = StatCard("Good posture", "#27500A")
        self.bad_card = StatCard("Bad posture", "#791F1F")
        self.alerts_card = StatCard("Times notified", "#412402")

        stats_layout.addWidget(self.good_card)
        stats_layout.addWidget(self.bad_card)
        stats_layout.addWidget(self.alerts_card)

        content_layout.addWidget(chart_card, stretch=1)
        content_layout.addLayout(stats_layout, stretch=1)
        content.setLayout(content_layout)

        outer_layout.addLayout(header)
        outer_layout.addWidget(content)
        self.setLayout(outer_layout)

        self.camera_process = None
        self.access_token = None
        self.refresh_token = None
        self.summaries = []

        self.thread = None
        self.worker = None

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.fetch_summaries)

        self._draw_pie(50, 50)  # placeholder until first fetch completes

    def _legend_item(self, text, color):
        item = QLabel(f"● {text}")
        item.setStyleSheet(f"color: {color}; font-size: 14px;")
        return item

    def start_camera(self):
        env = os.environ.copy()
        env["POSTURE_ACCESS_TOKEN"] = self.access_token
        env["POSTURE_REFRESH_TOKEN"] = self.refresh_token

        self.camera_process = subprocess.Popen([str(CV_CLIENT_PYTHON), str(CV_CLIENT_MAIN)], env=env)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_camera(self):
        if self.camera_process:
            self.camera_process.terminate()
            self.camera_process = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def load_data(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.fetch_summaries()
        self.refresh_timer.start(REFRESH_INTERVAL_MS)

    def fetch_summaries(self):
        if not self.access_token:
            return

        self.thread = QThread()
        self.worker = SummaryFetchWorker(self.access_token)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.on_summaries_fetched)
        self.worker.failure.connect(self.on_fetch_failed)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def on_summaries_fetched(self, data):
        self.summaries = data
        recent = self.summaries[-3:]

        if not recent:
            return

        good = sum(x['time_in_good_posture'] for x in recent) / len(recent)
        bad = sum(x['time_in_bad_posture'] for x in recent) / len(recent)
        alerts = sum(x['times_notified'] for x in recent)

        total = good + bad
        good_pct = (good / total * 100) if total else 0
        bad_pct = (bad / total * 100) if total else 0
        good_mins = good / 60
        bad_mins = bad / 60

        self.good_card.set_values(f"{good_pct:.0f}%", f"{good_mins:.1f} min")
        self.bad_card.set_values(f"{bad_pct:.0f}%", f"{bad_mins:.1f} min")
        self.alerts_card.set_values(str(alerts))

        self._draw_pie(good_pct, bad_pct)

    def _draw_pie(self, good_pct, bad_pct):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.pie(
            [good_pct, bad_pct],
            colors=[GOOD_COLOR, BAD_COLOR],
            startangle=90,
            wedgeprops={"linewidth": 0},
        )
        ax.set_aspect("equal")
        self.canvas.draw()

    def on_fetch_failed(self, error_message):
        print(f"Failed to fetch summaries: {error_message}")

    @staticmethod
    def _stylesheet():
        return """
            #DashboardScreen { background-color: #FAF9F5; }
            #Title { font-size: 16px; font-weight: 600; color: #412402; }
            #StartButton {
                background-color: #BA7517; color: white; border: none;
                border-radius: 6px; padding: 0 14px; font-size: 13px; font-weight: 500;
            }
            #StartButton:hover { background-color: #9c6412; }
            #StartButton:disabled { background-color: #e0c193; color: #f5f0e6; }
            #StopButton {
                background-color: transparent; color: #6b7280;
                border: 1px solid #ece7dc; border-radius: 6px; padding: 0 14px; font-size: 13px;
            }
            #StopButton:disabled { color: #c9c9c9; }
            #ContentCard { background-color: transparent; }
            #ChartCard, #StatCard {
                background-color: #ffffff; border-radius: 8px;
            }
            #StatLabel { font-size: 13px; color: #9b968a; }
            #StatValue { font-size: 24px; font-weight: 500; }
            #StatSubvalue { font-size: 13px; color: #9b968a; }
        """