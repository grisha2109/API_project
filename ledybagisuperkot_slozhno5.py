import sys
import urllib.request
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from geocoder import geocode

class YandexMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Яндекс.Карта")
        self.setGeometry(100, 100, 650, 650)

        self.current_lon = 37.6175
        self.current_lat = 55.7558
        self.current_zoom = 12

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.ll_input = QLineEdit()
        self.ll_input.setPlaceholderText("Долгота,Широта")
        self.ll_input.setText(f"{self.current_lon},{self.current_lat}")

        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Масштаб (0–17)")
        self.z_input.setText(str(self.current_zoom))

        self.find_input = QLineEdit()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная", "Спутник"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self.load_map)

        self.load_btn = QPushButton("Загрузить карту")
        self.load_btn.clicked.connect(self.load_map)

        self.find_btn = QPushButton("Искать")
        self.find_btn.clicked.connect(self.find_object)

        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumSize(600, 450)
        self.map_label.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        self.map_label.setFocusPolicy(Qt.StrongFocus)

        layout.addWidget(QLabel("Координаты (ll):"))
        layout.addWidget(self.ll_input)
        layout.addWidget(QLabel("Масштаб (z):"))
        layout.addWidget(self.z_input)
        layout.addWidget(QLabel("Тема карты:"))
        layout.addWidget(self.theme_combo)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.map_label)
        layout.addWidget(QLabel("Введите адрес:"))
        layout.addWidget(self.find_input)
        layout.addWidget(self.find_btn)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.load_map()

    def get_layer(self):
        theme = self.theme_combo.currentIndex()
        if theme == 0:
            return "map"
        elif theme == 1:
            return "skl"
        else:
            return "sat"

    def load_map(self):
        try:
            ll_text = self.ll_input.text().strip()
            if not ll_text:
                raise ValueError("Введите координаты")
            lon_str, lat_str = ll_text.split(",")
            self.current_lon = float(lon_str)
            self.current_lat = float(lat_str)

            zoom_str = self.z_input.text().strip()
            self.current_zoom = int(zoom_str)

            # Проверка диапазонов
            if not (-180 <= self.current_lon <= 180):
                raise ValueError("Долгота вне диапазона")
            if not (-85 <= self.current_lat <= 85):
                raise ValueError("Широта вне диапазона")
            if not (0 <= self.current_zoom <= 17):
                raise ValueError("Масштаб вне диапазона 0-17")

            layer = self.get_layer()
            url = (f"https://static-maps.yandex.ru/1.x/"
                   f"?ll={self.current_lon:.6f},{self.current_lat:.6f}&z={self.current_zoom}&l={layer}&size=600,450")
            print(f"Загружаем: {url}")

            with urllib.request.urlopen(url) as response:
                data = response.read()

            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.map_label.setPixmap(pixmap)
            self.map_label.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить карту:\n{str(e)}")

    def find_object(self):
        try:
            address = self.find_input.text().strip()
            if not address:
                return
            toponym = geocode(address)
            toponym_point = toponym["Point"]['pos']
            lon, lat = map(float, toponym_point.split())
            self.current_lon = lon
            self.current_lat = lat
            self.ll_input.setText(f"{self.current_lon},{self.current_lat}")
            self.load_map()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не найдено:\n{str(e)}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_PageUp:
            self.zoom_in()
        elif key == Qt.Key_PageDown:
            self.zoom_out()
        elif key == Qt.Key_Up:
            self.move_map(0, 1)
        elif key == Qt.Key_Down:
            self.move_map(0, -1)
        elif key == Qt.Key_Left:
            self.move_map(-1, 0)
        elif key == Qt.Key_Right:
            self.move_map(1, 0)
        else:
            super().keyPressEvent(event)

    def move_map(self, delta_lon, delta_lat):
        try:
            zoom = self.current_zoom
            lon_shi = 360 / (2 ** zoom) * 0.5
            lat_shi = 180 / (2 ** zoom) * 0.5

            new_lon = self.current_lon + delta_lon * lon_shi
            new_lat = self.current_lat + delta_lat * lat_shi

            new_lon = max(-180, min(180, new_lon))
            new_lat = max(-85, min(85, new_lat))

            self.current_lon = new_lon
            self.current_lat = new_lat

            self.ll_input.setText(f"{self.current_lon:.6f},{self.current_lat:.6f}")
            self.load_map()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось переместить карту:\n{str(e)}")

    def zoom_in(self):
        if self.current_zoom < 17:
            self.current_zoom += 1
            self.z_input.setText(str(self.current_zoom))
            self.load_map()

    def zoom_out(self):
        if self.current_zoom > 0:
            self.current_zoom -= 1
            self.z_input.setText(str(self.current_zoom))
            self.load_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YandexMapApp()
    window.show()
    sys.exit(app.exec_())
