import queue
import time
from typing import Callable

from loguru import logger

from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.custom_action import CustomAction
from maa.define import MaaAdbInputMethodEnum, MaaAdbScreencapMethodEnum
from maa.context import Context

from src.utils.configs import cfg
from src.utils.paths import asset_path
from src.utils.adb import (
    start_server,
    restart,
    connect_adb_devices,
    filter_online_devices,
    same_device,
)
from src.utils.click import STOP
from src.utils.model import StopException, DeviceNotFoundError

# 设备等待参数(单次轮询约3~4秒;需要重连端口/重启ADB的轮次会更慢)
POLL_INTERVAL = 2
# 指定设备连续多少次未上线后,改为试用其它可连接设备(约1~3分钟)
DEVICE_FALLBACK_ATTEMPTS = 15
# 每隔多少次重启一次ADB服务器(约1~3分钟)
ADB_RESTART_INTERVAL = 15
# 等待设备的总上限,超过则明确失败并告警(约5~20分钟,期间可随时停止)
DEVICE_WAIT_MAX_ATTEMPTS = 160


class MyCustomAction(CustomAction):
    name: str

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        return False

    def stop(self) -> None:
        pass


# 输入方式: 含 MaaTouch, 否则拖动类手势会被游戏忽略
INPUT_METHODS = MaaAdbInputMethodEnum.All
# 说明: 不要只开 AdbShell —— 它走 adb shell input 合成事件, 游戏对"拖动/滑动"类手势
# (主线位置旋盘、章节横滑等)不响应; All 让框架优先使用 MaaTouch 真实触摸流。


class TaskerManager:
    resource: Resource
    controller: AdbController
    tasker: Tasker
    custon_action: dict = {}
    init_flag_queue: queue.Queue = queue.Queue()
    # 设备等待失败等需要提示用户时的回调,由界面注册
    error_callback: Callable = None

    def __init__(self) -> None:
        pass

    def init(self) -> None:
        Toolkit.init_option(cfg.tool_kit_option)
        # Toolkit.init_option(user_path)

        # 输入方式: 不要只开 AdbShell —— 它走 adb shell input 合成事件, 游戏对"拖动/滑动"
        # 类手势不认(主线位置旋盘、章节横滑等会没反应); All 让框架优先用 MaaTouch 真实触摸流。
        self.resource = Resource()
        res_job = self.resource.post_bundle(asset_path("resource"))
        res_job.wait()
        device = self._wait_device()
        self.controller = AdbController(
            adb_path=device.adb_path,
            address=device.address,
            screencap_methods=device.screencap_methods,
            input_methods=INPUT_METHODS,
            config={},
            # config=device.config,
        )
        conn_job = self.controller.post_connection()
        conn_job.wait()
        if not conn_job.succeeded:
            raise ConnectionError(f"设备连接失败: {device.address}")
        self.tasker = Tasker()
        # self.tasker = Tasker(notification_handler=MyNotificationHandler())
        self.tasker.bind(self.resource, self.controller)
        self._register_custom_action()
        self.init_flag_queue.put(1)
        logger.info("初始化成功!!!")

    def _find_devices(self):
        """优先使用Maa自动检测,回退到自带ADB;只返回真正在线的设备"""
        devices = Toolkit.find_adb_devices()
        if not devices:
            devices = Toolkit.find_adb_devices(cfg.adb_dir)
        return filter_online_devices(devices)

    def _wait_device(self):
        """优先直接连接所选设备,失败则轮询查找,可被停止操作取消"""
        if cfg.adb_address:
            device = self._build_selected_device()
            ok, reason = self._try_connect(cfg.adb_address)
            if ok:
                logger.info(f"已连接所选ADB设备: {cfg.adb_address}")
                return device
            logger.warning(
                f"所选设备 {cfg.adb_address} 连接失败: {reason},等待设备上线..."
            )
        return self._wait_device_polling()

    def _try_connect(self, address: str):
        """真实连接一次以确认设备可用,返回(是否成功, 失败原因)"""
        try:
            controller = AdbController(
                adb_path=cfg.adb_dir,
                address=address,
                screencap_methods=MaaAdbScreencapMethodEnum.All,
                input_methods=INPUT_METHODS,
                config={},
            )
            job = controller.post_connection()
            job.wait()
            if job.succeeded:
                return True, ""
            return False, f"连接失败: {address}"
        except Exception as e:
            return False, str(e)

    def _notify_error(self, message: str) -> None:
        """把失败原因告知界面(未注册回调时只记录日志)"""
        if self.error_callback is None:
            return
        try:
            self.error_callback(message)
        except Exception as e:
            logger.warning(f"错误通知回调执行失败: {e}")

    def _build_selected_device(self):
        from maa.toolkit import AdbDevice

        return AdbDevice(
            name=cfg.adb_address,
            adb_path=cfg.adb_dir,
            address=cfg.adb_address,
            screencap_methods=MaaAdbScreencapMethodEnum.All,
            input_methods=INPUT_METHODS,
            config={},
        )

    def _wait_device_polling(self):
        """轮询查找ADB设备:所选设备优先,长时间未上线时回退到其它可连接设备,带超时保护"""
        logger.info("尝试寻找ADB设备")
        start_server()
        connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)
        attempt = 0
        fallback_tried: set[str] = set()
        while True:
            attempt += 1
            devices = self._find_devices()
            if cfg.adb_address:
                for device in devices:
                    if same_device(device.address, cfg.adb_address):
                        return device
            elif devices:
                return devices[0]

            if attempt == 1 or attempt % 5 == 0:
                connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)
                if cfg.adb_address:
                    logger.info(
                        f"等待指定ADB设备 {cfg.adb_address} 上线,已尝试{attempt}次..."
                    )
                elif attempt == 1:
                    logger.info("未找到ADB设备,请确认模拟器已启动...")
            if attempt % ADB_RESTART_INTERVAL == 0:
                logger.info(f"已尝试{attempt}次,重启ADB服务器...")
                restart()
                connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)

            # 所选设备长时间未上线: 试用其它设备,只采纳真正能连上的,避免死等
            if cfg.adb_address and attempt >= DEVICE_FALLBACK_ATTEMPTS:
                for device in devices:
                    if device.address in fallback_tried:
                        continue
                    fallback_tried.add(device.address)
                    logger.warning(
                        f"指定设备 {cfg.adb_address} 未上线,尝试改用 {device.address}"
                    )
                    ok, reason = self._try_connect(device.address)
                    if ok:
                        logger.warning(
                            f"已改用设备 {device.address},如需固定请在设置中重新选择"
                        )
                        return device
                    logger.debug(f"{device.address} 不可用: {reason}")

            if attempt >= DEVICE_WAIT_MAX_ATTEMPTS:
                if cfg.adb_address:
                    msg = (
                        f"等待ADB设备超时({attempt}次): 指定设备 {cfg.adb_address} 未上线,"
                        "且没有其它可连接设备"
                    )
                else:
                    msg = (
                        f"等待ADB设备超时({attempt}次): 未发现可用设备,"
                        "请确认模拟器已启动"
                    )
                logger.error(msg)
                self._notify_error(msg)
                raise DeviceNotFoundError(msg)

            if not STOP.empty():
                raise StopException("取消等待ADB设备")
            time.sleep(POLL_INTERVAL)

    def add_action(self, name: str):
        def warp_action(custon_action: type[MyCustomAction]):
            self.custon_action[name] = custon_action
            logger.debug(f"load {name}")
            original_run = custon_action.run

            def warp_custom_stop(*args, **kwargs):
                try:
                    return original_run(*args, **kwargs)
                except StopException as e:
                    logger.warning("STOPPED!!!!")
                    return True

            custon_action.run = warp_custom_stop
            return custon_action

        return warp_action

    def _register_custom_action(self):
        for key, value in self.custon_action.items():
            self.resource.register_custom_action(key, value())  # type: ignore


TASKER_MANAGER = TaskerManager()


def list_adb_devices():
    """返回当前已连接的ADB设备列表(只包含真正在线的设备,避免界面选到幽灵端口)"""
    try:
        Toolkit.init_option(cfg.tool_kit_option)
        connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)
        devices = (
            Toolkit.find_adb_devices()
            or Toolkit.find_adb_devices(cfg.adb_dir)
            or []
        )
    except Exception as e:
        logger.warning(f"查找ADB设备失败: {e}")
        return []
    return filter_online_devices(devices)
