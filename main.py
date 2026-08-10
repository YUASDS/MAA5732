import os
import sys
import time
import shutil
import datetime
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget
from src.ui.theme import apply_theme

LOG_KEEP_DAYS = 7


def clean_old_logs(days=LOG_KEEP_DAYS):
    """清理logs目录中超过指定天数的日志文件"""
    cutoff = time.time() - days * 86400
    if not os.path.exists("logs"):
        return
    for name in os.listdir("logs"):
        path = os.path.join("logs", name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            continue


def clean_update_dir():
    """清理上次更新遗留的临时目录(仅打包环境)"""
    if getattr(sys, "frozen", False):
        update_dir = os.path.join(os.path.dirname(sys.executable), "update")
        if os.path.isdir(update_dir):
            shutil.rmtree(update_dir, ignore_errors=True)


now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
if not os.path.exists("logs"):
    os.makedirs("logs")
clean_old_logs()
clean_update_dir()
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
