import re
import time

from loguru import logger
from maa.context import Context
from maa.custom_action import CustomAction

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction

# 友情点商店 数量加号按钮与数量显示区域(基于界面探测)
SHOP_PLUS = (0.817, 0.669)
SHOP_QTY_ROI = [0.55, 0.56, 0.35, 0.13]

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
        logger.info(f"采购中心 开始")
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
        logger.info(f"采购中心 完成")
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
        self.purchase("搜索", 3)
        self.purchase("梦影", 1)
        self.purchase("回响", 2)
        self.purchase("监测",1)
        self.purchase("边界",10)
        self.purchase("狂乱", 10)
        self.purchase("狄斯", 10)
        self.purchase("记忆", 10)
        self.purchase("一阶", 40)
        self.purchase("低阶", 40)
        self.purchase("技能", 40)

    def purchase(self, name, num):
        click = self.clicker
        click.ocr_click(name)
        time.sleep(1)
        current = self.get_shop_num()
        if current is None:
            current = 1
        target = max(num, 1)
        stall = 0
        while current < target:
            click.click_rate(*SHOP_PLUS)
            time.sleep(0.6)
            new = self.get_shop_num()
            if new is None or new <= current:
                stall += 1
                if stall >= 2:
                    logger.warning(
                        f"{name} 数量无法增加到{target},当前{current},可能已达限购"
                    )
                    break
            else:
                stall = 0
                current = new
        click.ocr_click("购买", roi=[0.71, 0.75, 1, 1])
        click.click_blink()

    def get_shop_num(self):
        """读取友情点商店当前购买数量,读取失败返回None"""
        items = self.clicker.ocr_roi(SHOP_QTY_ROI, sleep_time=0.3)
        texts = [t for t, _, _ in items]
        for text in texts:
            if text.isdigit():
                return int(text)
        match = re.search(r"(\d+)", "".join(texts))
        return int(match.group(1)) if match else None

    def stop(self) -> None:

        pass
