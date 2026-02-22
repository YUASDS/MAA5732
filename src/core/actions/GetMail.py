from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class GetMail(MyCustomAction):
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
        logger.info(f"邮件领取 开始")
        clicker = Click(context)
        clicker.ocr_click("邮箱")
        clicker.ocr_click("快速处理")
        clicker.click_blink()
        clicker.return_home()
        logger.info("邮件领取 完成")
        return True

    def stop(self) -> None:

        pass
