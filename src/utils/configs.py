import json
import os
import time

from loguru import logger

from src.utils.paths import ASSETS_DIR, BASE_DIR, asset_path

# 动态参数
curr_dir = BASE_DIR
adb_dir = asset_path("adb", "adb.exe")
# 自带 adb 缺失时回退到系统 PATH 中的 adb,保证资源不完整时也能尝试连接
if not os.path.exists(adb_dir):
    adb_dir = "adb"
scrn_dir = os.path.join(BASE_DIR, "screenshot.png")  # 截图后用于识别
## 当前日期
formatted_today = time.strftime("%Y-%m-%d", time.localtime(time.time()))

# 任务流水线: (节点ID, 动作名, 下一节点ID),入口固定为节点"1"
PIPELINE_ORDER = [
    ("1", "StartToHomeAction", "3"),
    ("3", "Guild", "4"),
    ("4", "GetMail", "5"),
    ("5", "Purchase", "6"),
    ("6", "Construction", "7"),
    ("7", "Bureau", "8"),
    ("8", "Friends", "9"),
    ("9", "FarmMaterial", "10"),
    ("10", "Raid", "11"),
    ("11", "Supervision", None),
]

# 界面默认设置: [各任务开关, 各任务详细设置]
DEFAULT_SETTINGS = [
    {
        "Guild": True,
        "Raid": True,
        "StartToHomeAction": True,
        "Friends": True,
        "Purchase": True,
        "Supervision": True,
        "Construction": True,
        "Bureau": True,
        "GetMail": True,
        "FarmMaterial": False,
    },
    {
        "Purchase": {
            "ActivityShopcheckBox": False,
            "FreeShopcheckBox": True,
            "FriendShopcheckBox": True,
        },
        "Friends": {"AutoLikecheckBox": True, "FriendPointcheckBox": True},
        "Raid": {
            "RaidDarkcheckBox": False,
            "RaidFightcheckBox": False,
            "RaidRivercheckBox": False,
            "ActivityRaidcheckBox": True,
            "ResourceCombo": "异能源质",
            "ResourceLevelCombo": "4",
            "StromLevelCombo": "5",
        },
        "Guild": {"GuildCombo": "狄斯币"},
        "Supervision": {"RewardCombo": "体力"},
        "Bureau": {"ActionPosCombo": "每日任务", "DailyFirstcheckBox": True},
        "StartToHomeAction": {
            "ServerCheckcomboBox": "B服",
            "StartAPPcheckBox": True,
        },
        "FarmMaterial": {
            "SweepCountCombo": "3",
            "ProgressModeCombo": "自动",
            "ProgressCombo": "13",
        },
    },
]

# 配置文件缺失或字段不全时的兜底默认值
DEFAULT_CONFIG = {
    "sleep_time": 1.5,
    "settings": DEFAULT_SETTINGS,
    "game_path": "",
    "game_args": "",
    "auto_run": False,
    "after_finish": "无",
    "check_update": True,
    "dismissed_update": "",
    "adb_address": "",
    "activity_remaining": {"date": "", "items": []},
    # 材料刷取: 主线进度缓存(探测失败时兜底)
    "main_progress": "",
    # 管理局: 最近一次派"每日任务"的日期(YYYY-MM-DD),用于每天只派一次
    "bureau_daily_date": "",
}

CONFIG_PATH = asset_path("config", "config.json")


def _merge_settings(saved) -> list[dict]:
    """把保存的设置与默认值合并,缺失字段回退默认值,兼容旧版本配置文件"""
    if not (
        isinstance(saved, list)
        and len(saved) == 2
        and isinstance(saved[0], dict)
        and isinstance(saved[1], dict)
    ):
        logger.warning("配置文件中的 settings 结构异常,已使用默认设置")
        saved = [{}, {}]
    toggles = {**DEFAULT_SETTINGS[0], **saved[0]}
    details = {name: dict(value) for name, value in DEFAULT_SETTINGS[1].items()}
    for name, value in saved[1].items():
        if isinstance(value, dict) and name in details:
            details[name].update(value)
        else:
            details[name] = value
    return [toggles, details]


# 从Config取值，当前程序专用
def load_config() -> dict:
    """读取配置,文件缺失或损坏时使用内置默认值"""
    config = {**DEFAULT_CONFIG}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except FileNotFoundError:
        logger.warning(f"未找到配置文件 {CONFIG_PATH},使用默认设置")
    except (OSError, ValueError) as e:
        logger.warning(f"配置文件读取失败({e}),使用默认设置")
    config["settings"] = _merge_settings(config.get("settings"))
    return config


config = load_config()


class cfg:
    adb_dir = adb_dir
    scrn_dir = scrn_dir
    formatted_today = formatted_today
    curr_dir = BASE_DIR
    tool_kit_option = ASSETS_DIR
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
    activity_remaining = config.get("activity_remaining", {"date": "", "items": []})
    main_progress = config.get("main_progress", "")
    bureau_daily_date = config.get("bureau_daily_date", "")
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
        "activity_remaining": cfg.activity_remaining,
        "main_progress": cfg.main_progress,
        "bureau_daily_date": cfg.bureau_daily_date,
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(this_config, f, ensure_ascii=False)
