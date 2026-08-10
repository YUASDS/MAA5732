import queue
import threading
from loguru import logger
from typing import Callable
from src.core.actions import *
from src.core.TaskerManager import TASKER_MANAGER
from src.utils.parse import json2pipline
from src.utils.click import STOP
from src.utils.model import StopException


class TaskerThread(threading.Thread):
    task: dict
    task_queue = queue.Queue()
    change_func: Callable
    finish_func: Callable
    manual_stop = False

    def __init__(self, change_func: Callable, finish_func: Callable = None, name=None):
        threading.Thread.__init__(self, name=name)
        self.change_func = change_func
        self.finish_func = finish_func or (lambda: None)

    def run(self) -> None:
        while True:
            task = self.task_queue.get()
            try:
                TASKER_MANAGER.init()
                TASKER_MANAGER.tasker.post_task("1", task).wait().get()
            except StopException:
                logger.warning("任务已取消")
                self.change_func()
                continue
            except Exception as e:
                logger.exception(e)
                continue
            global STOP
            STOP.put(1)
            self.change_func()
            if not self.manual_stop:
                self.finish_func()

    def add_task(self, json_data: list[dict]):
        self.task_queue.put(json2pipline(json_data))
        self.manual_stop = False
        global STOP
        STOP.queue.clear()

    def cancle_task(self):
        logger.warning("START TO STOP!!!")
        self.manual_stop = True
        global STOP
        STOP.put(1)
        self.task_queue.queue.clear()
        if not TASKER_MANAGER.init_flag_queue.empty():
            logger.warning("START TO POST STOP!!!")
            TASKER_MANAGER.tasker.post_stop()
        return STOP
