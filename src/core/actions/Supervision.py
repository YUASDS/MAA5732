import time

from loguru import logger
from maa.context import Context
from maa.custom_action import CustomAction

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Supervision(MyCustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        """
        :param argv:
        :param context: 运行上下文
        :return: 是否执行成功。
        """
        logger.info(f"监察密令 开始")
        clicker = Click(context)
        #  点击危机管理-OCR识别率低
        clicker.click_rate(0.74, 0.89)
        clicker.ocr_click("监察密令")
        clicker.ocr_rate_click("深度监察密令",0.04, 0.06)
        clicker.ocr_click("任务")
        clicker.ocr_click("每日")
        clicker.TemplateMatch("一键领取.png")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("领取")
        clicker.ocr_rate_click("直接领取", x=0.1, y=0.1)
        clicker.ocr_click("每周")
        clicker.TemplateMatch("一键领取.png")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("密令", roi=[0.25, 0.25, 0.5, 0.6])
        clicker.TemplateMatch("一键领取.png")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("监察", roi=[0.5, 0.5, 1, 1])
        clicker.ocr_click("一键领取", roi=[0.5, 0.5, 1, 1])
        # clicker.ocr_click("批量选择", roi=[0.5, 0.5, 1, 1])
        # clicker.ocr_click("确定")
        clicker.click_rate(0.2, 0.3)
        clicker.return_home()
        logger.info(f"监察密令 结束")
        return True

    def stop(self) -> None:

        pass
