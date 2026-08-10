import json
import urllib.request
from loguru import logger

GITHUB_API_URL = "https://api.github.com/repos/YUASDS/MAA5732/releases/latest"


def check_update():
    """检查GitHub最新版本,返回(tag_name, html_url, body),失败返回(None, None, None)"""
    try:
        req = urllib.request.Request(
            GITHUB_API_URL, headers={"User-Agent": "MAA5732"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tag_name = str(data.get("tag_name", ""))
        html_url = str(data.get("html_url", ""))
        body = str(data.get("body", ""))
        return tag_name, html_url, body
    except Exception as e:
        logger.warning(f"检查更新失败: {e}")
        return None, None, None


def version_tuple(version: str) -> tuple:
    """将版本号字符串转换为可比较的元组,如 v0.1.10 -> (0, 1, 10)"""
    try:
        nums = []
        for part in str(version).strip("vV").split("."):
            num = ""
            for ch in part:
                if ch.isdigit():
                    num += ch
                else:
                    break
            nums.append(int(num) if num else 0)
        return tuple(nums)
    except Exception:
        return (0,)


def is_newer(latest: str, current: str) -> bool:
    return version_tuple(latest) > version_tuple(current)
