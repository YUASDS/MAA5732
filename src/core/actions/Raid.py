import json
import re
import time
import numpy as np
from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg, save_confg
from src.utils.click import Click, stop_sleep
from src.utils.model import StopException

# 扫荡界面加号/减号按钮位置(基于当前界面探测)
SWEEP_PLUS = (0.7164, 0.6458)
SWEEP_MINUS = (0.2875, 0.6458)
# 选择次数显示区域

SWEEP_COUNT_ROI = [0.25, 0.588, 0.1, 0.04]

SOURCE_ITEMS = ("异能源质", "诡秘源质", "坚韧源质", "狂暴源质", "精准源质", "启迪源质")

default_cfg = {
    "RaidRiver": True,
    "RaidDark": True,
    "ResourceCombo": "狄斯币",
    "ResourceLevelCombo": "4",
    "StromLevelCombo": "5",
    "ActivityRaidcheckBox": False,
}

action_dict = {}


def gold_fight(context: Context):
    clicker = Click(context)
    clicker.click_rate(0.9, 0.2)


name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Raid(MyCustomAction):
    action_dict = {
        "狄斯币": ["行动", "狂热"],
        "狂乱精粹": ["行动", "之种"],
        "技能模组": ["污染", "探查"],
        "重构碎片": ["污染", "极域"],
        "异能源质": ["废墟", "异能"],
        "诡秘源质": ["废墟", "诡秘"],
        "坚韧源质": ["废墟", "坚韧"],
        "狂暴源质": ["废墟", "狂暴"],
        "精准源质": ["废墟", "精准"],
        "启迪源质": ["废墟", "启迪"],
    }
    run_param: dict = default_cfg.copy()

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
        logger.info(f"副本 开始")
        action_param = json.loads(argv.custom_action_param)
        run_param = default_cfg.copy()
        if action_param != {}:
            run_param = action_param
            self.run_param = run_param
        clicker = Click(context)
        # 点击危机管理
        self.clicker = clicker
        clicker.click_rate(0.74, 0.89)
        if run_param.get("ActivityRaidcheckBox"):
            self.ActivityRaid()
        elif run_param["RaidRivercheckBox"]:
            self.RaidRiver()
        if run_param["RaidDarkcheckBox"]:
            self.RaidDark()
        if run_param["RaidFightcheckBox"]:
            self.RaidFight()
        logger.info(f"副本 完成")
        return True

    def RaidDark(self):
        clicker = self.clicker
        logger.info("RaidDark Start")
        # 进入战斗
        clicker.click_rate(0.9, 0.2)
        clicker.ocr_click("内海")
        clicker.swape([0.8, 0.5, 10, 10], [0.1, 0.3, 10, 10], 0.8)
        clicker.ocr_click("浊暗之阱")
        clicker.ocr_click("浊暗", roi=[0.25, 0, 0.75, 1])
        clicker.ocr_click("扫荡")
        clicker.click_blink()
        clicker.return_home()
        logger.info("RaidDark Finish")

    def RaidRiver(self):
        logger.info("RaidRiver Start")
        self.RiverFight("记忆风暴", "点")
        # MS-r5
        logger.info("RaidRiver Finish")

    def RaidFight(self):
        ResourceCombo = self.run_param["ResourceCombo"]
        logger.info(f"RaidFight Start Resource: {ResourceCombo}")
        self.RiverFight(*self.action_dict[ResourceCombo])
        logger.info("RaidFight Finish")

    def RiverFight(self, first_action, second_action):
        # 选择锈河副本 - 第一次点击的文本 第二次点击的文本
        level = self.run_param["ResourceLevelCombo"]
        clicker = self.clicker
        clicker.click_rate(0.9, 0.2)
        clicker.ocr_click("锈河")
        clicker.ocr_click(first_action)

        res = clicker.ocr_click(second_action)
        if first_action =="废墟" and level >= "4":
            level = "4"
        if first_action =="废墟" and not res:
            clicker.swape([0.1, 0.9, 10, 10], [0.12, 0.1, 10, 10], 1000)
            res = clicker.ocr_click(second_action)
        if second_action == "极域" and level >= "4":
            level = "3"
        if first_action == "记忆风暴":
            level = self.run_param["StromLevelCombo"]
            if level == "5":
                level = "MS"
                clicker.ocr_click(level, roi=[0, 0.5, 1, 1])
            else:
                clicker.click_rate(0.7, 0.3)
                clicker.ocr_click(level, roi=[0, 0.41, 1, 0.2])
        else:
            clicker.ocr_click(level, roi=[0.3, 0.5, 1, 1])

        clicker.ocr_click("连续扫荡")
        # 当体力副本无体力时
        detail = clicker.ocr_click("取消")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            logger.warning("资源不足 取消扫荡")
            return

        clicker.ocr_click("开始扫荡")
        stop_sleep(10)
        # 升级的情况
        clicker.click_rate(0.5, 0.1)
        clicker.ocr_click("完成")
        # 继续扫荡
        clicker.ocr_click("连续扫荡")
        # 当体力副本无体力时
        detail = clicker.ocr_click("取消")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            logger.warning("资源不足 取消扫荡")
            return
        clicker.ocr_click("开始扫荡")
        stop_sleep(10)
        # 升级的情况
        clicker.click_rate(0.5, 0.1)
        clicker.ocr_click("完成")
        clicker.return_home()

    def add_range(self, num):
        click = self.clicker
        for _ in range(num):
            res = click.TemplateMatch("ADD.png", 0.7)
        return res

    def reduce_range(self, num):
        click = self.clicker
        for _ in range(num):
            res = click.TemplateMatch("REDUCE.png", 0.7)
        return res

    def get_num(self):
        """读取扫荡界面当前选择次数,返回int,读取失败返回None"""
        click = self.clicker
        # 1) 区域直接识别
        roi = [
            int(SWEEP_COUNT_ROI[0] * cfg.width),
            int(SWEEP_COUNT_ROI[1] * cfg.height),
            int(SWEEP_COUNT_ROI[2] * cfg.width),
            int(SWEEP_COUNT_ROI[3] * cfg.height),
        ]

        # 2. 对指定区域进行OCR

        for _ in range(3):
            res = click.ocr_roi(SWEEP_COUNT_ROI)
            num = self._parse_num([t for t, _, _ in res])
            if num is not None:
                return num
            stop_sleep(0.5)
        # 2) 截取次数区域放大3倍后识别(数字过小OCR易漏)
        for _ in range(3):
            image = click.context.tasker.controller.post_screencap().wait().get()
            h, w = image.shape[:2]
            crop = image[
                int(0.585 * h) : int(0.68 * h),
                int(0.30 * w) : int(0.48 * w),
            ]
            big = np.repeat(np.repeat(crop, 3, axis=0), 3, axis=1)
            detail = click.context.run_recognition(
                "get_num_zoom",
                big,
                {"get_num_zoom": {"recognition": "OCR", "timeout": 10000}},
            )
            num = self._parse_num(self._ocr_texts(detail))
            if num is not None:
                return num
            stop_sleep(0.5)
        # 3) 整屏兜底
        detail = click.context.run_task(
            "get_num_full",
            {"get_num_full": {"recognition": "OCR", "timeout": 10000}},
        )
        return self._parse_num(self._ocr_texts(detail), allow_standalone=False)

    def _ocr_texts(self, detail):
        """从任务/识别结果中提取OCR文本列表"""
        if detail is None:
            return []
        if hasattr(detail, "nodes"):
            if not detail.nodes:
                return []
            raw = detail.nodes[-1].recognition.raw_detail
        else:
            raw = detail.raw_detail
        if not raw:
            return []
        return [item["text"] for item in raw.get("all", [])]

    def _parse_num(self, texts, allow_standalone=True):
        """从OCR文本列表解析选择次数,超过合理范围(1-20)视为误读"""
        if not texts:
            return None
        # 合并识别: "选择次数8"
        match = re.search(r"选择次数(\d+)", "".join(texts))
        if match:
            return self._clamp_num(int(match.group(1)))
        # 标签与数字分开: ["选择次数", "8"]
        for i, text in enumerate(texts):
            if "选择次数" in text:
                if i + 1 < len(texts) and texts[i + 1].isdigit():
                    return self._clamp_num(int(texts[i + 1]))
                digits = re.findall(r"\d+", text)
                if digits:
                    return self._clamp_num(int(digits[-1]))
                break
        # 独立完整数字词(如 "8"),非字符级匹配
        if allow_standalone:
            for text in texts:
                if text.isdigit():
                    num = int(text)
                    if 1 <= num <= 20:
                        return num
        return None

    def _clamp_num(self, num):
        return num if 1 <= num <= 20 else None

    def add_num(self):
        """点击扫荡次数加号,返回新次数,次数无变化(体力不足)返回None"""
        self.clicker.click_rate(*SWEEP_PLUS)
        stop_sleep(0.8)
        return self.get_num()

    def reduce_num(self):
        """点击扫荡次数减号,返回新次数"""
        self.clicker.click_rate(*SWEEP_MINUS)
        stop_sleep(0.8)
        return self.get_num()

    def _set_sweep_count(self, target):
        """将扫荡次数设置为target,连续两次无变化判定为体力不足,返回False"""
        current = self.get_num()
        if current is None:
            logger.warning("无法读取扫荡次数")
            return False
        stall = 0
        while current < target:
            new = self.add_num()
            if new is None or new <= current:
                stall += 1
                if stall >= 2:
                    logger.warning(f"扫荡次数无法增加到{target},当前{current},可能体力不足")
                    return False
            else:
                stall = 0
                current = new
        while current > target:
            new = self.reduce_num()
            if new is None or new >= current:
                stall += 1
                if stall >= 2:
                    logger.warning(f"扫荡次数无法减少到{target},当前{current}")
                    return False
            else:
                stall = 0
                current = new
        return current == target

    def _activity_list(self):
        """活动扫荡任务列表: 狄斯币/狂乱精粹/用户选择的源质/记忆风暴/技能模组/重构碎片"""
        user = self.run_param.get("ResourceCombo", "异能源质")
        source = user if user in SOURCE_ITEMS else "异能源质"
        return [
            ("狄斯币", "行动", "狂热", False),
            ("狂乱精粹", "行动", "之种", False),
            (source, "废墟", self.action_dict[source][1], False),
            ("记忆风暴", "记忆风暴", "点", True),
            ("技能模组", "污染", "探查", False),
            ("重构碎片", "污染", "极域", False),
        ]

    def ActivityRaid(self):
        """活动扫荡: 各项各扫3次,体力不足或手动停止时记录剩余任务,当日再次运行则完成剩余"""
        remaining = self._load_remaining()
        if remaining:
            logger.info(f"恢复上次剩余任务: {', '.join(item[0] for item in remaining)}")
        else:
            remaining = self._activity_list()
        for i, item in enumerate(remaining):
            try:
                ok = self._sweep_item_once(item)
            except StopException:
                # 手动停止: 当前项扫荡已开始则视为完成,否则保留
                started = getattr(self, "_sweep_started", False)
                keep = remaining[i:] if not started else remaining[i + 1 :]
                self._save_remaining(keep)
                logger.warning(
                    f"手动停止,记录剩余任务: {', '.join(item[0] for item in keep)}"
                )
                raise
            if not ok:
                self._save_remaining(remaining[i:])
                logger.warning(f"体力不足,记录剩余任务: {', '.join(item[0] for item in remaining[i:])}")
                break
        else:
            self._clear_remaining()
            logger.info("活动扫荡全部完成")
        return True

    def _load_remaining(self):
        data = cfg.activity_remaining or {}
        if data.get("date") == cfg.formatted_today and data.get("items"):
            return list(data["items"])
        return []

    def _save_remaining(self, items):
        cfg.activity_remaining = {"date": cfg.formatted_today, "items": items}
        save_confg()

    def _clear_remaining(self):
        cfg.activity_remaining = {"date": "", "items": []}
        save_confg()

    def _sweep_item_once(self, item):
        """活动扫荡单项: 进入关卡→选等级→连续扫荡→次数设为3→开始扫荡,体力不足返回False"""
        self._sweep_started = False
        name, first, second, is_storm = item
        clicker = self.clicker
        logger.info(f"活动扫荡: {name}")
        clicker.click_rate(0.9, 0.2)
        clicker.ocr_click("锈河")
        clicker.ocr_click(first)
        res = clicker.ocr_click(second)
        # if first =="废墟" and level >= "4":
        #     level = "4"
        if first == "废墟" and not res:
            clicker.swape([0.1, 0.9, 10, 10], [0.12, 0.1, 10, 10], 1000)
            res = clicker.ocr_click(second)
        if not res or not res.status.succeeded:
            logger.warning(f"{name} 关卡未找到")
            clicker.return_home()
            return False
        if is_storm:
            level = self.run_param.get("StromLevelCombo", "5")
            if level == "5":
                clicker.click_rate(0.9, 0.7)
                clicker.ocr_click("MS", roi=[0, 0.5, 1, 1])
            else:
                clicker.click_rate(0.7, 0.3)
                clicker.ocr_click(level, roi=[0, 0.41, 1, 0.2])
        else:
            level = self.run_param.get("ResourceLevelCombo", "5")
            if first =="废墟" and level >= "4":
                level = "4"
            if second =="极域" and level >= "3":
                level = "3"
            clicker.ocr_click(level, roi=[0.3, 0.5, 1, 1])
        clicker.ocr_click("连续扫荡")
        # 当体力副本无体力时
        detail = clicker.ocr_click("取消")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            logger.warning("资源不足 取消扫荡")
            return False
        if not self._set_sweep_count(3):
            clicker.back()
            clicker.return_home()
            return False
        detail = clicker.ocr_click("开始扫荡")
        if not detail or not detail.status.succeeded:
            logger.warning(f"{name} 开始扫荡失败")
            clicker.back()
            clicker.return_home()
            return False
        self._sweep_started = True
        stop_sleep(12)
        clicker.click_rate(0.5, 0.1)
        clicker.ocr_click("完成")
        clicker.return_home()
        return True
    def stop(self) -> None:

        pass
