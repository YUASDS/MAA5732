import queue
import threading
import time
from loguru import logger
from typing import Callable
from src.core.actions import *
from src.core.TaskerManager import TASKER_MANAGER
from src.utils.parse import json2pipline
from src.utils.click import STOP
from src.utils.model import StopException

# 单个任务的执行超时(1小时),超过视为失败,保证线程不永久悬挂
TASK_TIMEOUT = 3600


class TaskerThread(threading.Thread):
    task: dict
    task_queue = queue.Queue()
    change_func: Callable
    finish_func: Callable
    manual_stop = False
    _busy = False

    def __init__(self, change_func: Callable, finish_func: Callable = None, name=None):
        threading.Thread.__init__(self, name=name)
        self.change_func = change_func
        self.finish_func = finish_func or (lambda: None)

    def run(self) -> None:
        global STOP
        initialized = False
        while True:
            task = self.task_queue.get()
            self._busy = True
            completed = False
            try:
                if not initialized:
                    TASKER_MANAGER.init()
                    initialized = True
                job = TASKER_MANAGER.tasker.post_task("1", task)
                deadline = time.time() + TASK_TIMEOUT
                while not job.done and time.time() < deadline:
                    if not STOP.empty():
                        TASKER_MANAGER.tasker.post_stop()
                    time.sleep(0.5)
                job.get()
                completed = job.succeeded
            except StopException:
                logger.warning("任务已取消")
                initialized = False
            except Exception as e:
                logger.exception(e)
                initialized = False
            finally:
                self._busy = False
                STOP.put(1)
                self.change_func()
            if completed and not self.manual_stop:
                self.finish_func()

    def is_busy(self) -> bool:
        """线程是否正在执行任务(初始化或任务执行中)"""
        return self._busy

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
