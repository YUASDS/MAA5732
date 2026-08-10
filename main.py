import os
import sys
import datetime
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget
from src.ui.theme import apply_theme

now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
if not os.path.exists("logs"):
    os.makedirs("logs")
logger.add(f"logs/{now_time}.log")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MyWidget()
    window.show()

    try:
        app.exec()
    except Exception as e:
        logger.exception(e)
