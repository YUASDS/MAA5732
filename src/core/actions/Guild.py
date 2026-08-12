import time

from loguru import logger
from maa.context import Context


from src.utils.configs import cfg
from src.utils.click import Click, stop_sleep
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Guild(MyCustomAction):

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
        logger.info(f"工会捐赠 开始")
        click = Click(context)
        click.check_return_home()
        # 整备中心
        click.click_rate(0.829, 0.911)
        # 秘盟
        click.click_rate(0.9, 0.3)
        # 首次进入 领取奖励
        click.click_rate(0.5, 0.08)
        stop_sleep(2)
        click.ocr_rate_click("签到", 0.9, 0.7)
        click.ocr_rate_click("秘盟捐赠", 0.671, 0.833)
        click.ocr_click("全部", roi=[0, 0, 0.3, 1])
        click.click_blink()
        click.return_home()
        logger.info(f"工会捐赠 完成")
        return True

    def stop(self) -> None:

        pass
