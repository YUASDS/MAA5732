import re
import subprocess

# PIPE
from subprocess import DEVNULL, PIPE
from loguru import logger
from src.utils.configs import cfg as cfg

# 常见模拟器ADB端口
EMULATOR_ADDRESSES = [
    "127.0.0.1:16384",  # MuMu模拟器
    "127.0.0.1:16416",
    "127.0.0.1:16448",
    "127.0.0.1:5555",  # 通用/雷电
    "127.0.0.1:5557",
    "127.0.0.1:7555",  # 雷电模拟器
    "127.0.0.1:62001",  # 夜神模拟器
    "127.0.0.1:62025",
    "127.0.0.1:21503",  # 网易MuMu?
]


def adb_run(cmd, **kwargs):
    """运行adb命令,不弹出命令行窗口"""
    kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
    return subprocess.run(cmd, **kwargs)


def change_size(adb_adress):
    result = adb_run(
        [cfg.adb_dir, "-s", adb_adress, "shell", "wm", "size"],
        stdout=PIPE,
        stderr=PIPE,
    )
    pat = re.compile(r"\d{1,5}")
    width, height = pat.findall(result.stdout.decode())
    cfg.width, cfg.height = int(width), int(height)


def restart():
    adb_run(
        [cfg.adb_dir, "kill-server"],
        stdout=PIPE,
        stderr=PIPE,
    )
    adb_run(
        [cfg.adb_dir, "start-server"],
        stdout=PIPE,
        stderr=PIPE,
    )


def start_server():
    adb_run(
        [cfg.adb_dir, "start-server"],
        stdout=PIPE,
        stderr=PIPE,
    )


def connect_adb_devices(addresses=None):
    """尝试连接常见模拟器端口及指定地址的ADB设备,已连接的跳过"""
    targets = list(EMULATOR_ADDRESSES)
    if addresses:
        for address in addresses:
            if address and address not in targets:
                targets.append(address)
    if not targets:
        return
    try:
        result = adb_run(
            [cfg.adb_dir, "devices"],
            stdout=PIPE,
            stderr=PIPE,
            timeout=10,
        )
        known = set()
        for line in result.stdout.decode(errors="ignore").splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] != "offline":
                known.add(parts[0])
    except Exception:
        known = set()
    for address in targets:
        if address in known:
            continue
        try:
            result = adb_run(
                [cfg.adb_dir, "connect", address],
                stdout=PIPE,
                stderr=PIPE,
                timeout=10,
            )
        except Exception:
            continue
        if (
            result.returncode == 0
            and "connected" in result.stdout.decode(errors="ignore")
        ):
            logger.debug(f"ADB设备已连接: {address}")


# 常见模拟器进程名(按优先级)
EMULATOR_PROCESSES = [
    "MuMuVMMHeadless.exe",  # MuMu模拟器虚拟机(核心)
    "MuMuNxMain.exe",       # MuMu模拟器主程序
    "MuMuNxDevice.exe",     # MuMu设备进程
    "MuMuRemoteService.exe",  # MuMu远程服务
    "NoxVMHandle.exe",      # 夜神模拟器
    "LdVBoxHeadless.exe",   # 雷电模拟器
    "HD-Player.exe",        # 蓝叠模拟器
]


def close_emulator():
    """关闭模拟器:结束游戏进程→adb emu kill→结束常见模拟器进程"""
    logger.info("尝试关闭模拟器")
    # 1) 结束本程序启动的游戏/模拟器进程(含子进程树)
    if cfg.game_process and cfg.game_process.poll() is None:
        try:
            result = adb_run(
                ["taskkill", "/F", "/T", "/PID", str(cfg.game_process.pid)],
                stdout=PIPE,
                stderr=PIPE,
            )
            if result.returncode == 0:
                logger.info("已关闭游戏进程")
        except Exception as e:
            logger.warning(f"关闭游戏进程失败: {e}")
    # 2) 尝试 adb emu kill(优先所选设备,再默认端口)
    for address in ([cfg.adb_address] if cfg.adb_address else []) + [None]:
        try:
            cmd = [cfg.adb_dir, "emu", "kill"]
            if address:
                cmd = [cfg.adb_dir, "-s", address, "emu", "kill"]
            result = adb_run(cmd, stdout=PIPE, stderr=PIPE)
            if result.returncode == 0:
                logger.info(f"已发送关闭模拟器指令: {address or '默认'}")
        except Exception as e:
            logger.warning(f"关闭模拟器失败: {e}")
    # 3) 结束常见模拟器进程(MuMu等不响应adb emu kill时的兜底)
    for name in EMULATOR_PROCESSES:
        try:
            result = adb_run(
                ["taskkill", "/F", "/IM", name],
                stdout=PIPE,
                stderr=PIPE,
            )
            if result.returncode == 0:
                logger.info(f"已关闭模拟器进程: {name}")
        except Exception as e:
            logger.warning(f"关闭进程失败 {name}: {e}")
