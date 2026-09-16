# -*- coding: utf-8 -*-
"""管理局: 派遣 + 领取体力

派遣流程: 危机管理 -> 管理局 -> 派遣 -> 一键领取 -> 选地点 -> 一键派遣。

界面参数(与"任务设置"栏控件同名, 由 src/utils/parse.py 作为 custom_action_param 传入):
  ActionPosCombo      派遣地点下拉框的值
  DailyFirstcheckBox  勾选后, 每天第一次派遣去"每日任务", 之后才用下拉框的地点
"""
import json
import time

from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click, stop_sleep
from src.utils.configs import cfg, save_confg

name = __file__.split("\\")[-1].split(".")[0]

# 派遣地点: 每日任务(每天一次的额外奖励) 辛迪加 新城 里湾 砂海
DAILY_POS = "每日任务"
# 键名与界面 Bureau_* 控件保持一致,作为界面参数缺失时的兜底
default_cfg = {
    "ActionPosCombo": DAILY_POS,
    "DailyFirstcheckBox": True,
}
# 每日任务用掉后记录日期(YYYY-MM-DD),当天不再重复去每日任务
DAILY_DATE_KEY = "bureau_daily_date"


def today_str() -> str:
    """当前日期(YYYY-MM-DD)

    刻意不用 cfg.formatted_today: 那是进程启动时的快照, 软件跨零点常驻时
    日期不会翻页, 会一直停在启动那天。
    """
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


@TASKER_MANAGER.add_action(name)
class Bureau(MyCustomAction):

    def run(
        self,
        context: Context,
        argv: MyCustomAction.RunArg,
    ) -> bool:
        """
        :param argv:
        :param context: 运行上下文
        :return: 是否执行成功。
        """
        run_param = self._load_param(argv.custom_action_param)
        pos = run_param["ActionPosCombo"] or DAILY_POS
        # 今天的第一次派遣是否去"每日任务"(每天只去一次, 之后按下拉框的地点派遣)
        first_today = bool(run_param["DailyFirstcheckBox"]) and not self._used_today()
        if first_today:
            logger.info(f"管理局: 今天还没派遣过, 本次去「{DAILY_POS}」")
            pos = DAILY_POS
        logger.info(f"管理局 开始")
        clicker = Click(context)
        #  点击危机管理-OCR识别率低
        clicker.click_rate(0.74, 0.89)
        clicker.ocr_click("管理局")
        clicker.ocr_click("派遣")
        clicker.ocr_click("一键领取")
        clicker.click_rate(0.9, 0.6)
        clicker.ocr_click(pos)
        clicker.ocr_click("一键")
        if first_today:
            # 派遣一旦发出去, 每天一次的"每日任务"就用掉了: 即使随后被手动停止或
            # 体力领取失败也不回滚, 否则重复回退反而会漏掉真正的每日奖励。
            self._mark_used()
        # 加载派遣动画
        stop_sleep(3)
        clicker.back()
        # 体力
        clicker.click_rate(0.156, 0.458)
        clicker.ocr_click("领取", roi=[0, 0, 1, 0.6])
        clicker.click_rate(0.25, 0.76)
        clicker.ocr_click("领取", roi=[0, 0.6, 1, 1])
        clicker.click_blink()
        clicker.click_blink()
        clicker.return_home()
        logger.info(f"管理局 完成")
        return True

    # ------------------------------------------------------------ 每日任务标记
    @staticmethod
    def _used_today() -> bool:
        """今天的"每日任务"是否已经派遣过"""
        return cfg.bureau_daily_date == today_str()

    @staticmethod
    def _mark_used() -> None:
        """记录今天已经派遣过"每日任务",避免同一天重复选择"""
        today = today_str()
        if cfg.bureau_daily_date == today:
            return
        cfg.bureau_daily_date = today
        save_confg()
        logger.info(f"管理局: 已记录今天的「{DAILY_POS}」,今天后续派遣按下拉框地点")

    # ------------------------------------------------------------ 参数
    def _load_param(self, raw) -> dict:
        """解析界面参数并与默认值合并,缺失字段回退默认值"""
        param = self._to_dict(raw)
        pos = param.get("ActionPosCombo") or default_cfg["ActionPosCombo"]
        return {
            "ActionPosCombo": pos,
            "DailyFirstcheckBox": bool(
                param.get("DailyFirstcheckBox", default_cfg["DailyFirstcheckBox"])
            ),
        }

    @staticmethod
    def _to_dict(raw) -> dict:
        """把参数转换为dict,兼容框架传入的JSON字符串或已解析的对象"""
        value = raw
        for _ in range(3):
            if isinstance(value, dict):
                return value
            if not isinstance(value, str) or not value:
                break
            try:
                value = json.loads(value)
            except ValueError:
                break
        if raw not in (None, ""):
            logger.warning(f"管理局参数无法解析,使用默认参数: {raw!r}")
        return {}

    def stop(self) -> None:

        pass
