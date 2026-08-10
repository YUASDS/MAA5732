import hashlib
import json
import os
import zipfile
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


def get_download_info():
    """获取最新版下载信息,优先exe,否则zip
    返回(类型, 文件名, 下载地址, sha256),类型为"exe"/"zip",失败返回(None, None, None, None)"""
    try:
        req = urllib.request.Request(
            GITHUB_API_URL, headers={"User-Agent": "MAA5732"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        exe_asset = None
        zip_asset = None
        for asset in data.get("assets", []):
            name = str(asset.get("name", ""))
            lower = name.lower()
            if lower.endswith(".exe"):
                exe_asset = asset
            elif lower.endswith(".zip"):
                zip_asset = asset
        for kind, asset in (("exe", exe_asset), ("zip", zip_asset)):
            if asset is None:
                continue
            name = str(asset.get("name", ""))
            digest = str(asset.get("digest", ""))
            sha256 = digest.split(":")[-1] if digest.startswith("sha256:") else ""
            return kind, name, str(asset.get("browser_download_url", "")), sha256
        return None, None, None, None
    except Exception as e:
        logger.warning(f"获取下载信息失败: {e}")
        return None, None, None, None


def download_file(url, dest, progress_cb=None):
    """下载文件到dest,progress_cb(已下载字节, 总字节)回调,返回文件sha256"""
    sha = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "MAA5732"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
                sha.update(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    progress_cb(downloaded, total)
    return sha.hexdigest()


def verify_sha256(path, expected):
    if not expected:
        return True
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            sha.update(chunk)
    return sha.hexdigest() == expected


def extract_zip(zip_path, dest_dir):
    """解压zip到dest_dir,返回包内exe文件名,失败返回None"""
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    exe_name = None
    for root, _, files in os.walk(dest_dir):
        for name in files:
            if name.lower().endswith(".exe"):
                exe_name = os.path.join(root, name)
                break
        if exe_name:
            break
    return exe_name


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
