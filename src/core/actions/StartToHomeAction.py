import time
from loguru import logger

from maa.context import Context

from src.utils.configs import cfg
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class StartToHomeAction(MyCustomAction):

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
        logger.info(f"{name} Start")
        clicker = Click(context)
        if cfg.settings[1][name]["StartAPPcheckBox"]:
            clicker.start_5732(cfg.settings[1][name]["ServerCheckcomboBox"])
            time.sleep(25)
        clicker.ocr_rate_click("系统公告", 0.1, 0.1, 20, 20)
        detail = clicker.ocr_click("进入管理局")
        if not detail or not detail.status.succeeded:
            time.sleep(10)
            clicker.ocr_click("进入管理局")
        # 等待进入
        time.sleep(30)
        # 处理广告
        while True:
            detail = clicker.ocr_rate_click("今日不再弹出",0.1, 0.1, 20, 20)
            status = detail.status.succeeded  # type: ignore
            logger.debug(f"Click:今日不再弹出 {status}")
            if not status:
                break
        # 领取月卡
        detail = clicker.ocr_click("领取",roi=[0.5, 0.5, 0.9, 0.9])
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.click_blink()
        # 领取月卡
        detail = clicker.ocr_click("贵宾")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.click_blink()
        # 情绪检测
        test_detail = clicker.ocr_rate_click("累计奖励", 0.625, 0.55)
        time.sleep(10)
        if test_detail and test_detail.status.succeeded:
            clicker.back()
        clicker.ocr_click("确定")
        clicker.ocr_rate_click("购买礼包", 0.902, 0.062)
        logger.info(f"{name} Finish")
        return True

    def stop(self) -> None:
        pass
