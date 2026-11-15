import time
import queue
import os
import shlex
import random
import subprocess
import json

from loguru import logger
from maa.context import Context
from maa.define import TaskDetail, Status, MaaStatusEnum
from maa.pipeline import (
    JActionType,
    JRecognitionType,
    JClick,
    JOCR,
    JSwipe,
    JStartApp,
    JTemplateMatch,
)

from src.utils.configs import cfg
from src.utils.model import StopException
from src.utils.paths import asset_path

STOP = queue.Queue()
STOP.put(1)

# 圈选标注的按钮坐标库（由 screenshot_gui.py 圈选生成）
BUTTONS_DB = asset_path("config", "buttons.json")

# MaaFw 3.0 扁平 pipeline 字段 -> 5.16 嵌套结构
_REC_FIELDS = {"expected", "roi", "template", "threshold", "green_mask", "roi_offset",
               "order_by", "index", "method", "replace", "only_rec", "model", "color_filter"}
_ACT_FIELDS = {"target", "target_offset", "begin", "end", "duration", "package", "contact",
               "pressure", "starting", "input_text", "exec", "args", "cmd", "custom_action",
               "custom_action_param", "key"}
_TOP_FIELDS = {"timeout", "next", "on_error", "rate_limit", "enabled", "inverse",
               "pre_delay", "post_delay", "repeat", "repeat_delay", "max_hit", "focus"}


def _v5_pipeline(flat: dict) -> dict:
    """把 MAA 3.0 扁平 pipeline 转成 5.16 嵌套结构。"""
    out = {}
    recog = flat.get("recognition")
    action = flat.get("action")

    if isinstance(recog, str):
        param = {k: v for k, v in flat.items() if k in _REC_FIELDS}
        # 5.16 里 expected/template/threshold 都是 list
        if isinstance(param.get("expected"), str):
            param["expected"] = [param["expected"]]
        if isinstance(param.get("template"), str):
            param["template"] = [param["template"]]
        if isinstance(param.get("threshold"), (int, float)):
            param["threshold"] = [param["threshold"]]
        out["recognition"] = {"type": recog, "param": param}

    if isinstance(action, str):
        param = {k: v for k, v in flat.items() if k in _ACT_FIELDS}
        out["action"] = {"type": action, "param": param}

    for k, v in flat.items():
        if k in _TOP_FIELDS:
            out[k] = v
    return out


def _run_task(context, entry: str, flat_override: dict):
    """封装 run_task，自动把扁平 pipeline 转成 5.16 嵌套结构。"""
    return context.run_task(entry, _v5_pipeline(flat_override))


def _run_recognition(context, entry: str, image, flat_override: dict):
    """封装 run_recognition，自动把扁平 pipeline 转成 5.16 嵌套结构。"""
    return context.run_recognition(entry, image, _v5_pipeline(flat_override))


def load_buttons_db():
    """读取按钮坐标库，失败返回空 dict"""
    try:
        with open(BUTTONS_DB, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


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

    def _screencap(self):
        """截取当前屏幕，返回 numpy 图像"""
        return self.context.tasker.controller.post_screencap().wait().get()

    @control_tragger
    def click_rate(self, x, y, offset_x=5, offset_y=5):
        stop_sleep(cfg.sleep_time)
        target = self.trans_from_rate_to_position(
            x, y, offset_x=offset_x, offset_y=offset_y
        )
        detail = self.context.run_action_direct(
            JActionType.Click, JClick(target=target)
        )
        if detail and not detail.success:
            logger.warning(f"Click Failed @ {target}")
        logger.debug(f"Clicked {target}")
        return detail

    @control_tragger
    def ocr_click(self, text, sleep_time=cfg.sleep_time, roi=None):
        if roi is None:
            roi = [0, 0, 0, 0]
        stop_sleep(sleep_time)
        if roi != [0, 0, 0, 0]:
            roi = [
                roi[0] * cfg.width,
                roi[1] * cfg.height,
                roi[2] * cfg.width,
                roi[3] * cfg.height,
            ]
        logger.debug(f"StartClick: {text}")
        image = self._screencap()
        reco = self.context.run_recognition_direct(
            JRecognitionType.OCR, JOCR(expected=[text], roi=roi), image
        )
        if not reco or not reco.hit:
            logger.warning(f"Click_{text} Failed (not found)")
            return None
        act = self.context.run_action_direct(
            JActionType.Click, JClick(), box=reco.box
        )
        logger.debug(f"Click_{text} Finish @ {reco.box}")
        return act

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
        dur = int(duration * 1000) if duration < 1 else int(duration)
        logger.debug(f"StartSwape:{start} {end} {dur}ms")
        detail = self.context.run_action_direct(
            JActionType.Swipe,
            JSwipe(begin=start, end=[end], duration=[dur]),
        )
        if detail and not detail.success:
            logger.warning("Swipe Failed")
        logger.debug("Swipe Finish")
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
        if roi != [0, 0, 0, 0]:
            roi = [
                roi[0] * cfg.width,
                roi[1] * cfg.height,
                roi[2] * cfg.width,
                roi[3] * cfg.height,
            ]
        stop_sleep(sleep_time)
        logger.debug(f"StartSearch: {text}")
        image = self._screencap()
        reco = self.context.run_recognition_direct(
            JRecognitionType.OCR, JOCR(expected=[text], roi=roi), image
        )
        if not reco or not reco.hit:
            logger.warning(f"Search_{text} Failed")
            return None
        logger.debug(f"Search_{text} Finish")
        return self.click_rate(x, y, offset_x, offset_y)

    @control_tragger
    def ocr(
        self,
        range=0.5,
        sleep_time=cfg.sleep_time,
    ):
        stop_sleep(sleep_time)
        logger.debug(f"StartOcr")
        image = self._screencap()
        reco = self.context.run_recognition_direct(
            JRecognitionType.OCR, JOCR(), image
        )
        if not reco:
            return {}
        res_dict = {}
        for r in reco.all_results:
            if hasattr(r, "text") and getattr(r, "score", 0) > range:
                res_dict[r.text] = r.score
        return res_dict

    @control_tragger
    def ocr_roi(self, roi, sleep_time=cfg.sleep_time):
        """在指定比例区域[ x, y, w, h ]内OCR,返回[(text, score, box), ...]"""
        stop_sleep(sleep_time)
        roi = [
            roi[0] * cfg.width,
            roi[1] * cfg.height,
            roi[2] * cfg.width,
            roi[3] * cfg.height,
        ]
        logger.debug(f"StartOcrRoi: {roi}")
        image = self._screencap()
        reco = self.context.run_recognition_direct(
            JRecognitionType.OCR, JOCR(roi=roi), image
        )
        if not reco:
            return []
        return [
            (r.text, getattr(r, "score", 0), list(r.box))
            for r in reco.all_results
            if hasattr(r, "text")
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
        detail = self.context.run_action_direct(
            JActionType.StartApp, JStartApp(package=package)
        )
        if detail and not detail.success:
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
        logger.debug(f"StartTemplateMatch:{template} {threshold}")
        image = self._screencap()
        reco = self.context.run_recognition_direct(
            JRecognitionType.TemplateMatch,
            JTemplateMatch(
                template=[template],
                roi=roi,
                threshold=[threshold],
                green_mask=green_mask,
            ),
            image,
        )
        if not reco or not reco.hit:
            logger.warning(f"TemplateMatch Failed: {template}")
            return None
        act = self.context.run_action_direct(
            JActionType.Click, JClick(), box=reco.box
        )
        logger.debug(f"TemplateMatch Finish @ {reco.box}")
        return act

    @control_tragger
    def smart_click(
        self,
        text: str,
        template: str = None,
        roi: list[float] = None,
        threshold: float = 0.7,
        sleep_time=cfg.sleep_time,
    ):
        """优化版点击：优先模板匹配(快)，失败再退化为 ROI 内 OCR(慢但稳)。

        - template: 模板图文件名(相对 assets/resource/image/)，如 "领取.png"
        - roi: 比例坐标 [x, y, w, h]，用于限制识别区域，避免整屏扫描
        """
        if roi is None:
            roi = [0, 0, 0, 0]
        # 1) 模板匹配优先
        if template:
            detail = self.TemplateMatch(template, threshold, roi=roi)
            if detail and detail.success:
                return detail
            logger.warning(f"smart_click: 模板 {template} 未命中, 回退 OCR")
        # 2) ROI 内 OCR 兜底
        return self.ocr_click(text, sleep_time=sleep_time, roi=roi)

    @control_tragger
    def smart_click_until_gone(
        self,
        text: str,
        template: str = None,
        roi: list[float] = None,
        threshold: float = 0.7,
        max_times: int = 20,
    ):
        """循环点击直到目标消失(找不到)或达到上限。

        适用于需要点多次的场景：
        - 逐个收菜/逐个领取（点一次少一个，点到找不到为止）
        - 购买加号（点一次数量+1，配合外部判断数量）
        每次优先模板匹配，找不到就视为"点完了"正常返回。
        """
        if roi is None:
            roi = [0, 0, 0, 0]
        for i in range(max_times):
            stop_sleep(cfg.sleep_time)
            if template:
                detail = self.TemplateMatch(template, threshold, roi=roi)
            else:
                detail = self.ocr_click(text, roi=roi)
            if not detail or not detail.success:
                logger.info(f"smart_click_until_gone: {text} 已消失, 共点击 {i} 次")
                return True
        logger.warning(f"smart_click_until_gone: {text} 点击 {max_times} 次后仍在")
        return True

    @control_tragger
    def db_click(self, btn_name: str):
        """从坐标库查按钮中心坐标直接点击（零识别，最快）。

        找不到该按钮名时返回 None（不会点击），调用方应兜底或跳过。
        """
        db = load_buttons_db()
        if btn_name not in db:
            logger.warning(f"db_click: 坐标库中没有按钮 '{btn_name}'")
            return None
        cx, cy = db[btn_name]["center"]
        logger.debug(f"db_click: {btn_name} -> ({cx}, {cy})")
        return self.click_rate(cx, cy)

    @control_tragger
    def db_or_ocr(self, btn_name: str, text: str, roi=None):
        """查库点击优先（快），坐标库没有该按钮则 OCR 兜底（慢但能用）。

        用法: clicker.db_or_ocr("点击后进入连续扫荡", "连续扫荡")
        """
        res = self.db_click(btn_name)
        if res:
            return res
        return self.ocr_click(text, roi=roi)
