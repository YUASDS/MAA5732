import json
import os
import time

# 动态参数
curr_dir = os.getcwd()
adb_dir = os.path.join(curr_dir, "assets", "adb", "adb.exe")
scrn_dir = os.path.join(curr_dir, "screenshot.png")  # 截图后用于识别
## 当前日期
formatted_today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
#! 以上参数在引用时需要使用类似config.ocr_dir的格式
base_template = """{
            "0": {
                "action": "custom",
                "custom_action": "Nothing"
            },
            "1": {
                "action": "custom",
                "custom_action": "StartToHomeAction",
                "custom_action_param": "StartToHomeActionCustom",
                "next": "3"
            },
            "2": {
                "action": "custom",
                "custom_action": "Nothing",
                "next": "3"
            },
            "3": {
                "action": "custom",
                "custom_action": "Guild",
                "custom_action_param": "GuildCustom",
                "next": "4"
            },
            "4": {
                "action": "custom",
                "custom_action": "GetMail",
                "next": "5"
            },
            "5": {
                "action": "custom",
                "custom_action": "Purchase",
                "custom_action_param": "PurchaseCustom",
                "next": "6"
            },
            "6": {
                "action": "custom",
                "custom_action": "Construction",
                "custom_action_param": "ConstructionCustom",
                "next": "7"
            },
            "7": {
                "action": "custom",
                "custom_action": "Bureau",
                "next": "8"
            },
            "8": {
                "action": "custom",
                "custom_action": "Friends",
                "custom_action_param": "FriendsCustom",
                "next": "9"
            },
            "9": {
                "action": "custom",
                "custom_action": "Raid",
                "custom_action_param": "RaidCustom",
                "next": "10"
            },
            "10": {
                "action": "custom",
                "custom_action": "Supervision",
                "custom_action_param": "SupervisionCustom"
            }
        }"""


# 从Config取值，当前程序专用
def load_config():
    confg_path = os.path.join(curr_dir, "assets", "config", "config.json")
    with open(confg_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


config = load_config()


class cfg:
    adb_dir = adb_dir
    scrn_dir = scrn_dir
    formatted_today = formatted_today
    curr_dir = os.getcwd()
    tool_kit_option = os.path.join(curr_dir, "assets")
    width = 1280
    height = 720
    sleep_time = config["sleep_time"]
    settings = config["settings"]
    game_path = config.get("game_path", "")
    game_args = config.get("game_args", "")
    auto_run = config.get("auto_run", False)
    after_finish = config.get("after_finish", "无")
    check_update = config.get("check_update", True)
    dismissed_update = config.get("dismissed_update", "")
    adb_address = config.get("adb_address", "")
    game_process = None


def save_confg():
    this_config = {
        "sleep_time": cfg.sleep_time,
        "settings": cfg.settings,
        "game_path": cfg.game_path,
        "game_args": cfg.game_args,
        "auto_run": cfg.auto_run,
        "after_finish": cfg.after_finish,
        "check_update": cfg.check_update,
        "dismissed_update": cfg.dismissed_update,
        "adb_address": cfg.adb_address,
    }
    with open(
        os.path.join(curr_dir, "assets", "config", "config.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(this_config, f, ensure_ascii=False)
