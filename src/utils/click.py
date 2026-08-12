import time
import queue
import os
import shlex
import random
import subprocess

from loguru import logger
from maa.context import Context
from maa.define import TaskDetail, Status, MaaStatusEnum

from src.utils.configs import cfg
from src.utils.model import StopException

STOP = queue.Queue()
STOP.put(1)


def control_tragger(func):
    def func_wrapper(*args, **kwargs):
        global STOP
        tragger = STOP.empty()
        if not tragger:
            raise StopException("STOPPING!!!!")
        return func(*args, **kwargs)

    return func_wrapper


def stop_sleep(seconds):
    """可被停止操作打断的等待,停止时抛StopException"""
    end = time.time() + seconds
    while time.time() < end:
        global STOP
        if not STOP.empty():
            raise StopException("STOPPING!!!!")
        time.sleep(0.2)


def _adb_online(address):
    """检查指定ADB设备是否在线"""
    try:
        result = subprocess.run(
            [cfg.adb_dir, "-s", address, "shell", "echo", "ok"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return result.returncode == 0
    except Exception:
        return False


def start_by_exe():
    """根据配置的游戏地址和附加参数启动游戏,已运行则跳过"""
    if not cfg.game_path:
        logger.warning("未设置游戏地址")
        return False
    if not os.path.exists(cfg.game_path):
        logger.warning(f"游戏地址不存在: {cfg.game_path}")
        return False
    if cfg.game_process and cfg.game_process.poll() is None:
        logger.info("游戏进程已在运行,跳过重复启动")
        return True
    if cfg.adb_address and _adb_online(cfg.adb_address):
        logger.info(f"ADB设备 {cfg.adb_address} 已在线,跳过启动模拟器")
        return True
    args = [cfg.game_path]
    if cfg.game_args:
        args.extend(shlex.split(cfg.game_args))
    logger.info(f"使用游戏地址启动")
    try:
        cfg.game_process = subprocess.Popen(
            args, cwd=os.path.dirname(cfg.game_path)
        )
        logger.info(f"游戏进程已启动, PID: {cfg.game_process.pid}")
        return True
    except Exception as e:
        logger.exception(f"启动游戏失败: {e}")
        return False


class Click:
    context: Context

    def __init__(self, context: Context) -> None:
        self.context = context

    def trans_from_rate_to_position(self, x, y, offset_x=5, offset_y=5):
        """
        Generate random x and y based on a normal distribution  within +- 12px.
        precondition x !=0.0
        Returns:
            List[float]: A list of generated coordinates [x, y, xx, yy].
        """
        x = round(cfg.width * x, 2)
        y = round(cfg.height * y, 2)
        return [x - offset_x, y - offset_y, offset_x, offset_y]

    @control_tragger
    def click_rate(self, x, y, offset_x=5, offset_y=5):
        stop_sleep(cfg.sleep_time)
        target = self.trans_from_rate_to_position(
            x, y, offset_x=offset_x, offset_y=offset_y
        )
        random_num = random.random()
        detail = self.context.run_task(
            f"just_click_{random_num}",
            {f"just_click_{random_num}": {"action": "Click", "target": target}},
        )
        if detail and not detail.status.succeeded:
            logger.warning(f"just_click_{random_num} Failed")
        logger.debug(f"Clicked {target}")
        return detail

    @control_tragger
    def ocr_click(self, text, sleep_time=cfg.sleep_time, roi=None):
        if roi is None:
            roi = [0, 0, 0, 0]
        stop_sleep(sleep_time)
        random_num = random.random()
        if roi != [0, 0, 0, 0]:
            roi = [
                roi[0] * cfg.width,
                roi[1] * cfg.height,
                roi[2] * cfg.width,
                roi[3] * cfg.height,
            ]
        logger.debug(f"StartClick: {text}")
        detail = self.context.run_task(
            f"{text}_{random_num}",
            {
                f"{text}_{random_num}": {
                    "timeout": 1500,
                    "recognition": "OCR",
                    "roi": roi,
                    "expected": text,
                    "action": "Click",
                }
            },
        )
        if detail and not detail.status.succeeded:
            logger.warning(f"Click_{text} Failed")
        logger.debug(f"Click_{text} Finish")
        return detail

    @control_tragger
    def return_home(self):
        logger.debug("ReturnHome Start")
        detail = self.click_rate(0.15, 0.061)
        logger.debug("ReturnHome Finish")
        return detail

    @control_tragger
    def back(self):
        logger.debug("Back Start")
        detail = self.click_rate(0.04, 0.06)
        logger.debug("Back Finish")
        return detail

    @control_tragger
    def click_blink(self):
        logger.debug("ClickBlink Start")
        detail = self.click_rate(0.6, 0.97)
        logger.debug("ClickBlink Finish")
        return detail

    @control_tragger
    def swape(self, start, end, duration):
        if start[0] < 1:
            start[0] = start[0] * cfg.width
            start[1] = start[1] * cfg.height
            end[0] = end[0] * cfg.width
            end[1] = end[1] * cfg.height
        stop_sleep(cfg.sleep_time)
        random_num = random.random()
        logger.debug(f"StartSwape_{random_num}:{start} {end}")

        detail = self.context.run_task(
            f"Swipe_{random_num}",
            {
                f"Swipe_{random_num}": {
                    "action": "Swipe",
                    "begin": start,
                    "end": end,
                    "duration": duration,
                }
            },
        )
        if detail and not detail.status.succeeded:
            logger.warning(f"StartSwape_{random_num} Failed")
        logger.debug(f"StartSwape_{random_num} Finish")
        return detail

    @control_tragger  # TODO : check_stage_return_home
    def check_stage_return_home(self, stage_name):
        stop_sleep(cfg.sleep_time)
        logger.debug(f"CheckStage_{stage_name} Start")
        detail = self.ocr_click(stage_name)
        logger.debug(f"CheckStage_{stage_name} Finish")
        return detail

    @control_tragger  
    def check_return_home(self):
        detail =self.return_home()
        if "局长信息" in self.ocr(0.5):
            detail = self.back()
        stop_sleep(cfg.sleep_time)
        return detail

    @control_tragger
    def ocr_rate_click(
        self, text, x, y, offset_x=5, offset_y=5, sleep_time=cfg.sleep_time, roi=None
    ):
        if roi is None:
            roi = [0, 0, 0, 0]
        stop_sleep(sleep_time)
        logger.debug(f"StartSearch: {text}")
        detail = self.context.run_task(
            text,
            {
                text: {
                    "timeout": 1500,
                    "recognition": "OCR",
                    "roi": roi,
                    "expected": text,
                }
            },
        )
        if detail and not detail.status.succeeded:
            logger.warning(f"Search_{text} Failed")
        logger.debug(f"Search_{text} Finish")
        if detail and detail.status.succeeded:
            return self.click_rate(x, y, offset_x, offset_y)
        return detail

    @control_tragger
    def ocr(
        self,
        range=0.5,
        sleep_time=cfg.sleep_time,
    ):
        stop_sleep(sleep_time)
        logger.debug(f"StartOcr")
        random_num = random.random()
        detail = self.context.run_task(
            f"Ocr_{random_num}",
            {
                f"Ocr_{random_num}": {
                    "timeout": 1500,
                    "recognition": "OCR",
                }
            },
        )
        if not detail:
            return
        last_node = detail.nodes[-1]
        raw_detail_list = last_node.recognition.raw_detail["all"]
        res_dict = {}
        for raw_detail in raw_detail_list:
            if raw_detail["score"] > range:
                res_dict[raw_detail["text"]] = raw_detail["score"]
        return res_dict

    @control_tragger
    def ocr_roi(self, roi, sleep_time=cfg.sleep_time):
        """在指定比例区域[ x, y, w, h ]内OCR,返回[(text, score, box), ...]"""
        stop_sleep(sleep_time)
        random_num = random.random()
        roi = [
            roi[0] * cfg.width,
            roi[1] * cfg.height,
            roi[2] * cfg.width,
            roi[3] * cfg.height,
        ]
        logger.debug(f"StartOcrRoi: {roi}")
        detail = self.context.run_task(
            f"OcrRoi_{random_num}",
            {
                f"OcrRoi_{random_num}": {
                    "timeout": 1500,
                    "recognition": "OCR",
                    "roi": roi,
                }
            },
        )
        if not detail or not detail.nodes:
            return []
        raw_detail_list = detail.nodes[-1].recognition.raw_detail["all"]
        return [
            (item["text"], item.get("score", 0), item.get("box", []))
            for item in raw_detail_list
        ]

    @control_tragger
    def start_5732(self, name):
        logger.debug("Start 5732")
        if cfg.game_path:
            start_by_exe()
            return
        trans_dict = {"B服": "bilibili", "官服": "cn"}
        server = trans_dict[name]
        package = (
            f"com.zy.wqmt.{server}/com.papegames.gamelib_unity.BaseUnityImplActivity"
        )
        detail = self.context.run_task(
            "Start 5732",
            {
                "Start 5732": {
                    "action": "StartApp",
                    "package": package,
                }
            },
        )
        if detail and not detail.status.succeeded:
            logger.warning("Start 5732 Failed")
        logger.debug("Start 5732 Finish")

    @control_tragger
    def TemplateMatch(
        self,
        template: str,
        threshold: float = 0.7,
        green_mask: bool = False,
        roi: list[float] = None,  # type:ignore
    ):
        "模板匹配"
        if roi is None:
            roi = [0, 0, 0, 0]
        stop_sleep(cfg.sleep_time)
        random_num = random.random()
        logger.debug(f"StartTemplateMatch_{random_num}:{template} {threshold}")
        detail = self.context.run_task(
            f"template_match_{random_num}",
            {
                f"template_match_{random_num}": {
                    "recognition": "TemplateMatch",
                    "action": "Click",
                    "template": template,
                    "roi": roi,
                    "threshold": threshold,
                    "green_mask": green_mask,
                }
            },
        )
        if detail and not detail.status.succeeded:
            logger.warning(f"TemplateMatch_{random_num} Failed")
        logger.debug(f"TemplateMatch_{random_num} Finish")
        return detail
