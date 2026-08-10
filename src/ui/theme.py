from PySide6.QtWidgets import QApplication

THEME = """
QWidget {
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #E6E9F0;
    background-color: #12141B;
}
QTabWidget { background: transparent; }
QTabWidget::pane {
    border: 1px solid #2A2F3D;
    border-radius: 10px;
    background-color: #171A23;
    top: -1px;
}
QTabBar::tab {
    background-color: transparent;
    color: #9AA3B5;
    padding: 8px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:hover { color: #E6E9F0; }
QTabBar::tab:selected {
    color: #00E0C6;
    background-color: #1E222D;
}
QGroupBox {
    background-color: #1E222D;
    border: 1px solid #2A2F3D;
    border-radius: 10px;
    margin-top: 12px;
    padding: 14px 12px 10px 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #00E0C6;
    font-weight: bold;
}
QStackedWidget { background: transparent; }
QCheckBox {
    spacing: 8px;
    color: #E6E9F0;
    padding: 2px 0;
}
QCheckBox:hover { color: #FFFFFF; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #3A4154;
    background-color: #12141B;
}
QCheckBox::indicator:hover { border-color: #00E0C6; }
QCheckBox::indicator:checked {
    background-color: #00E0C6;
    border-color: #00E0C6;
    image: url(assets/ui/check.png);
}
QCheckBox::indicator:disabled {
    background-color: #262B38;
    border-color: #343B4D;
}
QPushButton {
    background-color: #262B38;
    border: 1px solid #343B4D;
    border-radius: 6px;
    padding: 5px 14px;
    color: #E6E9F0;
}
QPushButton:hover { background-color: #2F3647; border-color: #00E0C6; }
QPushButton:pressed { background-color: #1D212C; }
QPushButton:disabled {
    color: #5A6274;
    background-color: #1E222D;
    border-color: #2A2F3D;
}
QPushButton#LinkStartButton {
    background-color: #00E0C6;
    border: none;
    border-radius: 8px;
    padding: 8px 30px;
    color: #0A0E14;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#LinkStartButton:hover { background-color: #2FE8D0; }
QPushButton#LinkStartButton:pressed { background-color: #00BFA8; }
QPushButton#LinkStartButton[running="true"] {
    background-color: #E85D75;
    color: #FFFFFF;
}
QPushButton#LinkStartButton[running="true"]:hover { background-color: #F0728A; }
QPushButton#LinkStartButton[running="true"]:pressed { background-color: #D14A62; }
QPushButton#BrowseButton, QPushButton#CheckUpdateButton {
    background-color: #00E0C6;
    border: none;
    border-radius: 6px;
    padding: 5px 14px;
    color: #0A0E14;
    font-weight: bold;
}
QPushButton#BrowseButton:hover, QPushButton#CheckUpdateButton:hover {
    background-color: #2FE8D0;
}
QComboBox {
    background-color: #12141B;
    border: 1px solid #3A4154;
    border-radius: 6px;
    padding: 4px 10px;
    color: #E6E9F0;
}
QComboBox:hover { border-color: #00E0C6; }
QComboBox:focus { border-color: #00E0C6; }
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
    image: url(assets/ui/down-arrow.png);
}
QComboBox QAbstractItemView {
    background-color: #1E222D;
    border: 1px solid #2A2F3D;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #00E0C6;
    selection-color: #0A0E14;
    outline: none;
}
QLineEdit {
    background-color: #12141B;
    border: 1px solid #3A4154;
    border-radius: 6px;
    padding: 5px 8px;
    color: #E6E9F0;
    selection-background-color: #00E0C6;
    selection-color: #0A0E14;
}
QLineEdit:hover { border-color: #00E0C6; }
QLineEdit:focus { border-color: #00E0C6; }
QTextBrowser {
    background-color: #0D0F15;
    border: 1px solid #2A2F3D;
    border-radius: 8px;
    padding: 6px;
    font-family: "Cascadia Mono", Consolas, "Microsoft YaHei UI", monospace;
    font-size: 12px;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #3A4154;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #00E0C6; }
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #3A4154;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #00E0C6; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QToolTip {
    background-color: #262B38;
    color: #E6E9F0;
    border: 1px solid #3A4154;
    padding: 4px 8px;
}
QMessageBox { background-color: #171A23; }
QMessageBox QPushButton { min-width: 80px; }
QDialog { background-color: #171A23; }
QLabel#UpdateTitleLabel {
    color: #00E0C6;
    font-size: 15px;
    font-weight: bold;
}
QWidget#TitleBar {
    background-color: #171A23;
}
QLabel#TitleLabel {
    color: #E6E9F0;
    font-size: 13px;
    font-weight: bold;
    padding-left: 4px;
}
QPushButton#TitleBarMinButton,
QPushButton#TitleBarMaxButton,
QPushButton#TitleBarCloseButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    color: #9AA3B5;
    font-size: 13px;
    padding: 0;
}
QPushButton#TitleBarMinButton:hover,
QPushButton#TitleBarMaxButton:hover {
    background-color: #2A2F3D;
    color: #E6E9F0;
}
QPushButton#TitleBarCloseButton:hover {
    background-color: #E85D75;
    color: #FFFFFF;
}
QPushButton#DownloadButton {
    background-color: #00E0C6;
    border: none;
    border-radius: 6px;
    padding: 6px 18px;
    color: #0A0E14;
    font-weight: bold;
}
QPushButton#DownloadButton:hover { background-color: #2FE8D0; }
QPushButton#DismissButton {
    background-color: transparent;
    border: none;
    color: #9AA3B5;
}
QPushButton#DismissButton:hover { color: #E6E9F0; }
"""


def apply_theme(app: QApplication):
    app.setStyleSheet(THEME)
