import time

from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click


name = __file__.split("\\")[-1].split(".")[0]


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
        logger.info(f"管理局 开始")
        clicker = Click(context)
        #  点击危机管理-OCR识别率低
        clicker.click_rate(0.74, 0.89)
        clicker.ocr_click("管理局")
        clicker.ocr_click("派遣")
        clicker.ocr_click("一键领取")
        clicker.click_rate(0.9, 0.6)
        clicker.ocr_click("一键")
        # 加载派遣动画
        time.sleep(3)
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

    def stop(self) -> None:

        pass
