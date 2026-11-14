import hashlib
import json
import os
import zipfile
import urllib.request
from pathlib import Path, PurePosixPath
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
    """只接受与发行包同名的主程序,避免误选旧版本或 assets/adb/adb.exe。"""
    expected_name = Path(zip_path).with_suffix(".exe").name
    with zipfile.ZipFile(zip_path, "r") as zf:
        candidates = [
            info for info in zf.infolist()
            if not info.is_dir()
            and PurePosixPath(info.filename.replace("\\", "/")).name.lower()
            == expected_name.lower()
        ]
        if len(candidates) != 1:
            logger.warning(f"更新包应包含唯一的 {expected_name},实际找到 {len(candidates)} 个")
            return None
        # 校验解压位置,确保选中的程序路径和实际落盘路径一致。
        destination = Path(dest_dir).resolve()
        for info in zf.infolist():
            relative = PurePosixPath(info.filename.replace("\\", "/"))
            if relative.is_absolute() or any(
                part in {".", ".."} or ":" in part for part in relative.parts
            ):
                raise ValueError(f"更新包包含无效路径: {info.filename}")
            target = destination.joinpath(*relative.parts).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError(f"更新包路径超出解压目录: {info.filename}")
        os.makedirs(destination, exist_ok=True)
        zf.extractall(dest_dir)
    return str(destination.joinpath(*PurePosixPath(
        candidates[0].filename.replace("\\", "/")
    ).parts))


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
