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
        动态识别屏幕内容，执行相应操作，最终到达游戏主界面。
        """
        logger.info(f"启动 开始")
        clicker = Click(context)

        # 启动应用
        if cfg.settings[1][name]["StartAPPcheckBox"]:
            clicker.start_5732(cfg.settings[1][name]["ServerCheckcomboBox"])
            time.sleep(30)  # 冷启动等待

        max_attempts = 60  # 防止死循环
        while max_attempts > 0:
            max_attempts -= 1
            screen_dict = clicker.ocr() or ""  # 获取当前屏幕所有文本
            screen_text = "".join(screen_dict)
            logger.debug(f"OCR识别结果: {screen_text}")
            # 管理局密钥
            if "管理局密钥" in screen_text:
                detail = clicker.ocr_click("领取")
                if detail and detail.status.succeeded:
                    logger.debug("已领取管理局密钥")
                clicker.back()
                time.sleep(1)
                clicker.back()
                time.sleep(1)
                continue
            # 处理系统公告弹窗
            if "系统公告" in screen_text:
                # 固定坐标点击关闭按钮（源自原ocr_rate_click坐标）
                clicker.click_rate(0.1, 0.1, 20, 20)
                time.sleep(1)
                continue

            # # 点击“进入管理局”
            if "进入管理局" in screen_text:
                detail = clicker.ocr_click("进入管理局")
                if detail and detail.status.succeeded:
                    logger.info("已点击『进入管理局』")
                    time.sleep(10)  # 等待加载
                continue

            # 关闭广告
            if "今日不再弹出" in screen_text:
                detail = clicker.click_rate(0.1, 0.1, 20, 20)  # 固定坐标
                if detail and detail.status.succeeded:
                    logger.debug("已关闭广告弹窗")
                time.sleep(1)
                continue

            # 领取月卡
            if "领取" in screen_text:
                # detail = clicker.ocr_click("领取", roi=[0.5, 0.5, 0.9, 0.9])
                # if detail and detail.status.succeeded:
                clicker.click_blink()  # 确认
                clicker.click_blink()
                logger.debug("已领取月卡")
                time.sleep(1)
                continue

            if "贵宾" in screen_text:
                detail = clicker.ocr_click("贵宾")
                if detail and detail.status.succeeded:
                    clicker.click_blink()
                    clicker.click_blink()
                    logger.debug("已领取贵宾奖励")
                    time.sleep(1)
                continue

            # 情绪检测
            if "累计奖励" in screen_text:
                clicker.click_rate(0.625, 0.55)  # 固定坐标点击
                time.sleep(2)
                clicker.back()  # 返回
                logger.debug("已处理情绪检测")
                continue

            # 公会战弹窗
            if "确定" in screen_text:
                clicker.ocr_click("确定")
                time.sleep(1)
                continue

            # 服装弹窗
            if "购买礼包" in screen_text:
                clicker.click_rate(0.902, 0.062)  # 固定坐标（礼包关闭按钮）
                logger.debug("已关闭购买礼包弹窗")
                time.sleep(1)
                continue
            if "生日" in screen_text:
                clicker.back()
                time.sleep(1)
                continue
            if "禁闭者" not in screen_text:
                clicker.back()
                time.sleep(1)
                continue
            # 判断是否已到达主界面
            if all(
                kw not in screen_text
                for kw in ["系统公告", "进入管理局", "今日不再弹出", "累计奖励"]
            ) and any(kw in screen_text for kw in ["禁闭者"]):
                logger.info("已到达游戏主界面")
                break

            # 若长时间未到达主界面，短暂休眠后继续识别
            time.sleep(0.5)

        else:
            logger.warning("超时未到达主界面，可能网络或加载异常")
            # 仍尝试执行后续收尾操作

        clicker.ocr_click("确定")
        clicker.click_rate(0.902, 0.062)

        logger.info(f"启动 结束")
        return True

    def stop(self) -> None:
        pass
