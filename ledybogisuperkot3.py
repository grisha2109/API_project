import sys
import urllib.request
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class YandexMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Яндекс.Карта")
        self.setGeometry(100, 100, 650, 600)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.ll_input = QLineEdit()
        self.ll_input.setPlaceholderText("Долгота,Широта")
        self.ll_input.setText("37.6175,55.7558")

        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Масштаб (0–17)")
        self.z_input.setText("12")

        self.load_btn = QPushButton("Загрузить карту")
        self.load_btn.clicked.connect(self.load_map)

        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumSize(600, 450)
        self.map_label.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")

        self.map_label.setFocusPolicy(Qt.StrongFocus)

        layout.addWidget(QLabel("Координаты (ll):"))
        layout.addWidget(self.ll_input)
        layout.addWidget(QLabel("Масштаб (z):"))
        layout.addWidget(self.z_input)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.map_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.load_map()

    def load_map(self):
        try:
            ll = self.ll_input.text().strip()
            z = self.z_input.text().strip()

            if not ll or not z:
                raise ValueError("Заполните поля")

            lon, lat = map(float, ll.split(","))
            zoom = int(z)

            if not (-180 <= lon <= 180) or not (-85 <= lat <= 85):
                raise ValueError("Некорректные координаты")

            if not (0 <= zoom <= 17):
                raise ValueError("Масштаб неверен")

            url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}&l=map&size=600,450"

            with urllib.request.urlopen(url) as response:
                data = response.read()

            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.map_label.setPixmap(pixmap)

            self.map_label.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить карту:\n{str(e)}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.zoom_in()
        elif event.key() == Qt.Key_PageDown:
            self.zoom_out()
        elif event.key() == Qt.Key_Up:
            self.move_map(0, 1)
        elif event.key() == Qt.Key_Down:
            self.move_map(0, -1)
        elif event.key() == Qt.Key_Left:
            self.move_map(-1, 0)
        elif event.key() == Qt.Key_Right:
            self.move_map(1, 0)
        else:
            super().keyPressEvent(event)

    def move_map(self, delta_lon, delta_lat):
        try:
            ll = self.ll_input.text().strip()
            lon, lat = map(float, ll.split(","))
            zoom = int(self.z_input.text())
            lon_shi = 360 / (2 ** zoom) * 0.25
            lat_shi = 180 / (2 ** zoom) * 0.25

            new_lon = lon + delta_lon * lon_shi
            new_lat = lat + delta_lat * lat_shi

            if new_lon < -180:
                new_lon = -180
            elif new_lon > 180:
                new_lon = 180

            if new_lat < -85:
                new_lat = -85
            elif new_lat > 85:
                new_lat = 85

            self.ll_input.setText(f"{new_lon:.6f},{new_lat:.6f}")
            self.load_map()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось переместить карту:\n{str(e)}")

    def zoom_in(self):
        try:
            current_zoom = int(self.z_input.text())
            max_zoom = 17
            new_zoom = min(current_zoom + 1, max_zoom)
            self.z_input.setText(str(new_zoom))
            self.load_map()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение масштаба.")

    def zoom_out(self):
        try:
            current_zoom = int(self.z_input.text())
            min_zoom = 0
            new_zoom = max(current_zoom - 1, min_zoom)
            self.z_input.setText(str(new_zoom))
            self.load_map()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение масштаба.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YandexMapApp()
    window.show()
    sys.exit(app.exec_())