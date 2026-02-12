import sys
import urllib.request
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, \
    QMessageBox, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from geocoder import geocode


class MapViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Карта")
        self.resize(650, 700)

        self.lon = 37.6175
        self.lat = 55.7558
        self.zoom = 12
        self.marker = None
        self.current_address = ""

        panel = QWidget()
        layout = QVBoxLayout()

        self.coord_field = QLineEdit()
        self.coord_field.setText(f"{self.lon},{self.lat}")

        self.zoom_field = QLineEdit()
        self.zoom_field.setText(str(self.zoom))

        self.search_field = QLineEdit()
        self.search_field.returnPressed.connect(self.locate)

        self.theme_select = QComboBox()
        self.theme_select.addItems(["обычная", "схема", "спутник"])
        self.theme_select.currentIndexChanged.connect(self.refresh)

        load_btn = QPushButton("Обновить")
        load_btn.clicked.connect(self.refresh)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.locate)

        clear_btn = QPushButton("Стереть метку")
        clear_btn.clicked.connect(self.drop_marker)
        clear_btn.setEnabled(False)

        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setMinimumSize(600, 450)
        self.display.setStyleSheet("border: 1px solid #aaa; background: #eee")
        self.display.setFocusPolicy(Qt.StrongFocus)

        self.status = QLabel("метка отсутствует")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color: #777; font-style: italic")

        self.address_field = QLabel("адрес не найден")
        self.address_field.setAlignment(Qt.AlignCenter)
        self.address_field.setStyleSheet("color: #006400; font-weight: bold")

        reset_btn = QPushButton("Сброс поискового результата")
        reset_btn.clicked.connect(self.reset_search)
        reset_btn.setEnabled(False)

        layout.addWidget(QLabel("координаты:"))
        layout.addWidget(self.coord_field)
        layout.addWidget(QLabel("масштаб:"))
        layout.addWidget(self.zoom_field)
        layout.addWidget(QLabel("стиль:"))
        layout.addWidget(self.theme_select)
        layout.addWidget(load_btn)
        layout.addWidget(self.display)
        layout.addWidget(self.status)
        layout.addWidget(QLabel("поиск:"))
        layout.addWidget(self.search_field)
        layout.addWidget(search_btn)
        layout.addWidget(clear_btn)
        layout.addWidget(self.address_field)
        layout.addWidget(reset_btn)

        panel.setLayout(layout)
        self.setCentralWidget(panel)

        # БЛОКИРУЕМ клавиши PgUp/PgDown для QComboBox
        self.theme_select.setFocusPolicy(Qt.NoFocus)

        self.refresh()
        self.display.setFocus()

    def layer(self):
        idx = self.theme_select.currentIndex()
        if idx == 0:
            return "map"
        elif idx == 1:
            return "skl"
        else:
            return "sat"

    def refresh(self):
        try:
            parts = self.coord_field.text().strip().split(",")
            self.lon = float(parts[0])
            self.lat = float(parts[1])
            self.zoom = int(self.zoom_field.text().strip())

            if not -180 <= self.lon <= 180:
                raise ValueError("долгота")
            if not -85 <= self.lat <= 85:
                raise ValueError("широта")
            if not 0 <= self.zoom <= 17:
                raise ValueError("масштаб")

            base = f"https://static-maps.yandex.ru/1.x/?ll={self.lon:.6f},{self.lat:.6f}&z={self.zoom}&l={self.layer()}&size=600,450"
            if self.marker:
                base += f"&pt={self.marker[0]:.6f},{self.marker[1]:.6f},pm2rdm"

            data = urllib.request.urlopen(base).read()
            img = QPixmap()
            img.loadFromData(data)
            self.display.setPixmap(img)

            for btn in self.findChildren(QPushButton):
                if btn.text() == "Стереть метку":
                    btn.setEnabled(self.marker is not None)
                    break
            for btn in self.findChildren(QPushButton):
                if btn.text() == "Сброс поискового результата":
                    btn.setEnabled(bool(self.current_address))
                    break

            if self.marker:
                self.status.setText(f"метка: {self.marker[0]:.4f}, {self.marker[1]:.4f}")
                self.status.setStyleSheet("color: #006400; font-weight: bold")
            else:
                self.status.setText("метка отсутствует")
                self.status.setStyleSheet("color: #777; font-style: italic")

        except Exception as e:
            QMessageBox.critical(self, "сбой", f"карта не загружена:\n{e}")

    def locate(self):
        try:
            query = self.search_field.text().strip()
            if not query:
                return
            result = geocode(query)
            pos = result["Point"]["pos"]
            x, y = map(float, pos.split())
            self.lon = x
            self.lat = y
            self.marker = (x, y)
            self.current_address = result.get("name", "") or result.get("description", "неизвестно")
            self.address_field.setText(self.current_address)
            self.coord_field.setText(f"{self.lon:.6f},{self.lat:.6f}")
            self.refresh()
            self.search_field.clear()
        except:
            QMessageBox.warning(self, "упс", "ничего не найдено")

    def drop_marker(self):
        self.marker = None
        self.refresh()

    def reset_search(self):
        self.current_address = ""
        self.address_field.setText("адрес не найден")
        self.marker = None
        self.refresh()

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_PageUp:
            self.zoom = min(17, self.zoom + 1)
            self.zoom_field.setText(str(self.zoom))
            self.refresh()
            return
        elif k == Qt.Key_PageDown:
            self.zoom = max(0, self.zoom - 1)
            self.zoom_field.setText(str(self.zoom))
            self.refresh()
            return
        elif k == Qt.Key_Up:
            self.shift(0, 1)
            return
        elif k == Qt.Key_Down:
            self.shift(0, -1)
            return
        elif k == Qt.Key_Left:
            self.shift(-1, 0)
            return
        elif k == Qt.Key_Right:
            self.shift(1, 0)
            return

        super().keyPressEvent(e)

    def shift(self, dx, dy):
        try:
            step_x = 360.0 / (2 ** (self.zoom + 8)) * abs(dx)
            step_y = 180.0 / (2 ** (self.zoom + 8)) * abs(dy)
            self.lon += dx * step_x * 100
            self.lat += dy * step_y * 100
            self.lon = max(-180, min(180, self.lon))
            self.lat = max(-85, min(85, self.lat))
            self.coord_field.setText(f"{self.lon:.6f},{self.lat:.6f}")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "сдвиг", f"не вышло:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MapViewer()
    win.show()
    sys.exit(app.exec_())
