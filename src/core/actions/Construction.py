from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click


name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Construction(MyCustomAction):
    name = __file__.split("\\")[-1].split(".")[0]

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
        logger.info(f"基建收菜 开始")
        clicker = Click(context)
        # 点击整备中心 OCR识别率低
        clicker.click_rate(0.829, 0.911)

        clicker.ocr_click("监管")
        clicker.ocr_click("收取")
        clicker.click_blink()
        clicker.ocr_click("监管终端")
        clicker.click_rate(0.9, 0.6)
        [clicker.click_rate(0.908, 0.889) for _ in range(40)]

        clicker.return_home()
        logger.info(f"基建收菜 完成")
        return True

    def stop(self) -> None:

        pass
