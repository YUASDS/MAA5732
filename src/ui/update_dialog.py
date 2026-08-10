from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from src.core import version


class UpdateDialog(QDialog):
    dismissed = Signal()
    download_requested = Signal()

    def __init__(self, latest, url, body, parent=None):
        super().__init__(parent)
        self.url = url
        self.setWindowTitle("发现新版本")
        self.setFixedSize(500, 430)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(12)

        title = QLabel(
            f"发现新版本 {latest},当前版本 {version}", self
        )
        title.setObjectName("UpdateTitleLabel")
        layout.addWidget(title)

        browser = QTextBrowser(self)
        browser.setPlainText(body if body else "暂无更新说明")
        layout.addWidget(browser, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.dismiss_btn = QPushButton("不再显示", self)
        self.dismiss_btn.setObjectName("DismissButton")
        later_btn = QPushButton("稍后再说", self)
        download_btn = QPushButton("下载更新", self)
        download_btn.setObjectName("DownloadButton")
        btn_row.addWidget(self.dismiss_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(later_btn)
        btn_row.addWidget(download_btn)
        layout.addLayout(btn_row)

        self.dismiss_btn.clicked.connect(self._on_dismiss)
        later_btn.clicked.connect(self.accept)
        download_btn.clicked.connect(self._on_download)

    def _on_download(self):
        self.download_requested.emit()
        self.accept()

    def _on_dismiss(self):
        self.dismissed.emit()
        self.accept()
