import time

from loguru import logger
from maa.context import Context
from maa.custom_action import CustomAction

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Purchase(MyCustomAction):
    clicker: Click

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
        logger.info(f"{name} Start")
        click = Click(context)
        self.clicker = click
        action_param = cfg.settings[1][name]
        #  点击危机管理-OCR识别率低
        click.click_rate(0.74, 0.89)
        click.ocr_click("采购办")
        if action_param["FreeShopcheckBox"]:
            self.free_shop()
        if action_param["FriendShopcheckBox"]:
            self.frends_shop()
        click.return_home()
        logger.info(f"{name} Finish")
        return True

    # 454750
    def free_shop(self):
        click = self.clicker
        click.ocr_click("精选礼包")
        click.ocr_click("精选推荐")
        # for _ in range(1):
        #     click.swape([0.965, 0.5, 10, 10], [0.5, 0.6, 10, 10], 1000)
        click.ocr_click("每日免费补给")
        click.ocr_click("购买")
        click.click_blink()
        # self.frends_shop()

    def frends_shop(self):
        click = self.clicker
        click.swape([0.1, 0.9, 10, 10], [0.12, 0.1, 10, 10], 1000)
        click.ocr_click("兑换中心")
        click.swape([0.1, 0.9, 10, 10], [0.12, 0.1, 10, 10], 1000)
        click.ocr_click("友情兑换")
        self.purchase("狂乱", 3)
        self.purchase("狄斯", 3)
        self.purchase("记忆", 3)

    # TODO
    def purchase(self, name, num):
        click = self.clicker
        click.ocr_click(name)
        for _ in range(num):
            res = click.TemplateMatch("ADD.png", 0.7)
        click.ocr_click("购买", roi=[0.5, 0.75, 1, 1])
        click.click_blink()

    def stop(self) -> None:

        pass
