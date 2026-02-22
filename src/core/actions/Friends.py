from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Friends(MyCustomAction):

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
        logger.info(f"好友 开始")
        clicker = Click(context)
        # 点击整备中心
        clicker.click_rate(0.829, 0.911)
        clicker.ocr_click("好友")
        # 领取
        clicker.click_rate(0.898, 0.861)
        # 赠送
        clicker.click_rate(0.898, 0.861)
        clicker.return_home()
        logger.info(f"好友 完成")
        return True

    def stop(self) -> None:

        pass
