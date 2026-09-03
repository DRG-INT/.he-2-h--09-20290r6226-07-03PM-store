"""
Kernel Event Viewer
Kernel események megtekintése és elemzése egyszerű GUI-val.
"""

import sys
from datetime import datetime

import requests
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class KernelEventViewer(QMainWindow):
    """Kernel események megtekintése"""

    event_added = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.clickhouse_host = "localhost"
        self.clickhouse_port = 8123
        self.events = []
        self.anomalies = []
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Felhasználói felület inicializálása"""
        self.setWindowTitle("Kernel Event Viewer")
        self.setGeometry(100, 100, 1400, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # Kontroll panel
        control_layout = QHBoxLayout()

        # Esemény típus szűrő
        self.event_filter = QComboBox()
        self.event_filter.addItems([
            "Összes",
            "sys_enter_open",
            "sys_enter_read",
            "sys_enter_write",
            "sys_enter_close",
            "do_fork",
            "do_exit",
            "kmalloc",
            "kfree",
            "handle_mm_fault"
        ])
        control_layout.addWidget(QLabel("Esemény típus:"))
        control_layout.addWidget(self.event_filter)

        # PID szűrő
        self.pid_filter = QLineEdit()
        self.pid_filter.setPlaceholderText("PID szűrő...")
        control_layout.addWidget(QLabel("PID:"))
        control_layout.addWidget(self.pid_filter)

        # Időszak szűrő
        self.time_range = QComboBox()
        self.time_range.addItems(["1 perc", "5 perc", "15 perc", "1 óra", "6 óra", "24 óra"])
        control_layout.addWidget(QLabel("Időszak:"))
        control_layout.addWidget(self.time_range)

        # Frissítés gomb
        self.refresh_btn = QPushButton("Frissítés")
        self.refresh_btn.clicked.connect(self.load_events)
        control_layout.addWidget(self.refresh_btn)

        # Automatikus frissítés
        self.auto_refresh = QPushButton("Auto: KI")
        self.auto_refresh.setCheckable(True)
        self.auto_refresh.clicked.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh)

        layout.addLayout(control_layout)

        # Splitter
        splitter = QSplitter(Qt.Vertical)

        # Események táblázat
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(7)
        self.events_table.setHorizontalHeaderLabels([
            "Időbélyeg", "PID", "TID", "CPU", "Esemény típus", "Időtartam (ns)", "Visszatérés"
        ])
        self.events_table.horizontalHeader().setStretchLastSection(True)
        self.events_table.setAlternatingRowColors(True)
        splitter.addWidget(self.events_table)

        # Riasztások szövegmező
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setFont(QFont("Courier", 10))
        self.alerts_text.setStyleSheet("background-color: #1a1a1a; color: #ff3333;")
        splitter.addWidget(self.alerts_text)

        layout.addWidget(splitter)

        # Státusbar
        self.statusBar().showMessage("Kész")

    def setup_timer(self):
        """Timer automatikus frissítéshez"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_events)

    def toggle_auto_refresh(self):
        """Automatikus frissítés be/ki"""
        if self.auto_refresh.isChecked():
            self.auto_refresh.setText("Auto: BE")
            self.timer.start(5000)  # 5 másodperc
        else:
            self.auto_refresh.setText("Auto: KI")
            self.timer.stop()

    def load_events(self):
        """Események betöltése ClickHouse-ból"""
        try:
            # Időszak konverzió
            time_range_map = {
                "1 perc": "1 MINUTE",
                "5 perc": "5 MINUTES",
                "15 perc": "15 MINUTES",
                "1 óra": "1 HOUR",
                "6 óra": "6 HOURS",
                "24 óra": "24 HOURS"
            }
            time_range = time_range_map.get(self.time_range.currentText(), "1 MINUTE")

            # Esemény típus szűrő
            event_filter = self.event_filter.currentText()
            where_clause = f"WHERE timestamp > now() - INTERVAL {time_range}"
            if event_filter != "Összes":
                where_clause += f" AND event_type = '{event_filter}'"

            # PID szűrő
            pid_filter = self.pid_filter.text().strip()
            if pid_filter.isdigit():
                where_clause += f" AND pid = {pid_filter}"

            # Query
            query = f"""
            SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm
            FROM kernel_events.kernel_events
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT 1000
            """

            response = requests.post(
                f"http://{self.clickhouse_host}:{self.clickhouse_port}/",
                params={"query": query},
                timeout=10
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []
                for line in lines[1:]:  # Első sor a fejléc
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        data.append(parts)

                self.display_events(data)
                self.statusBar().showMessage(f"Betöltve: {len(data)} esemény")

        except Exception as e:
            self.statusBar().showMessage(f"Hiba: {e!s}")

    def display_events(self, data):
        """Események megjelenítése"""
        self.events_table.setRowCount(len(data))

        for row, event in enumerate(data):
            # Időbélyeg
            timestamp = event[0]
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            self.events_table.setItem(row, 0, QTableWidgetItem(time_str))

            # PID, TID, CPU
            for i, value in enumerate(event[1:6], 1):
                self.events_table.setItem(row, i, QTableWidgetItem(str(value)))

            # Visszatérés
            retval = event[6]
            item = QTableWidgetItem(str(retval))
            if retval and int(retval) < 0:
                item.setBackground(QColor("#ffcccc"))
            self.events_table.setItem(row, 6, item)

    def add_alert(self, alert_data):
        """Riasztás hozzáadása"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {alert_data['alert_level']}: "
        alert_text += f"Kernel panic probability: {alert_data['panic_probability']:.2%}\n"

        self.alerts_text.append(alert_text)
        self.alerts_text.verticalScrollBar().setValue(
            self.alerts_text.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        """Bezárás esemény"""
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    viewer = KernelEventViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
