from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(38)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel(self)
        icon = QIcon()
        icon.addFile("assets/resource/image/logo.ico")
        self.icon_label.setPixmap(icon.pixmap(20, 20))
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("MAA5732", self)
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.min_button = self._make_button("Min", "\u2014")
        self.max_button = self._make_button("Max", "\u25a1")
        self.close_button = self._make_button("Close", "\u2715")
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

        self.min_button.clicked.connect(self.window().showMinimized)
        self.max_button.clicked.connect(self._toggle_max)
        self.close_button.clicked.connect(self.window().close)

    def _make_button(self, name, text):
        btn = QPushButton(text, self)
        btn.setObjectName(f"TitleBar{name}Button")
        btn.setFixedSize(32, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _toggle_max(self):
        window = self.window()
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if (
            self._drag_pos is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.window().move(
                event.globalPosition().toPoint() - self._drag_pos
            )

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_max()
