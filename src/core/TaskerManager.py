import queue
import time
from loguru import logger

from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.custom_action import CustomAction
from maa.define import MaaAdbInputMethodEnum
from maa.context import Context
from maa.notification_handler import NotificationHandler, NotificationType

from src.utils.configs import cfg
from src.utils.adb import start_server, restart, connect_adb_devices
from src.utils.click import STOP
from src.utils.model import StopException


class MyCustomAction(CustomAction):
    name: str

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        return False

    def stop(self) -> None:
        pass


class MyNotificationHandler(NotificationHandler):
    def on_resource_loading(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.ResourceLoadingDetail,
    ):
        print(f"on_resource_loading: {noti_type}, {detail}")

    def on_controller_action(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.ControllerActionDetail,
    ):
        print(f"on_controller_action: {noti_type}, {detail}")

    def on_tasker_task(
        self, noti_type: NotificationType, detail: NotificationHandler.TaskerTaskDetail
    ):
        print(f"on_tasker_task: {noti_type}, {detail}")

    def on_node_next_list(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.NodeNextListDetail,
    ):
        print(f"on_node_next_list: {noti_type}, {detail}")

    def on_node_recognition(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.NodeRecognitionDetail,
    ):
        print(f"on_node_recognition: {noti_type}, {detail}")

    def on_node_action(
        self, noti_type: NotificationType, detail: NotificationHandler.NodeActionDetail
    ):
        print(f"on_node_action: {noti_type}, {detail}")

    def on_unknown_notification(self, msg: str, details: dict):
        print(f"on_unknown_notification: {msg}, {details}")


class TaskerManager:
    resource: Resource
    controller: AdbController
    tasker: Tasker
    custon_action: dict = {}
    init_flag_queue: queue.Queue = queue.Queue()

    def __init__(self) -> None:
        pass

    def init(self) -> None:
        Toolkit.init_option(cfg.tool_kit_option)
        # Toolkit.init_option(user_path)

        self.resource = Resource()
        res_job = self.resource.post_bundle("assets/resource")
        res_job.wait()
        device = self._wait_device()
        self.controller = AdbController(
            adb_path=device.adb_path,
            address=device.address,
            screencap_methods=device.screencap_methods,
            input_methods=MaaAdbInputMethodEnum.AdbShell,
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
        """优先使用Maa自动检测,回退到自带ADB"""
        devices = Toolkit.find_adb_devices()
        if not devices:
            devices = Toolkit.find_adb_devices(cfg.adb_dir)
        return devices

    def _wait_device(self):
        """优先直接连接所选设备,失败则轮询查找,可被停止操作取消"""
        if cfg.adb_address:
            device = self._build_selected_device()
            try:
                controller = AdbController(
                    adb_path=device.adb_path,
                    address=device.address,
                    screencap_methods=device.screencap_methods,
                    input_methods=MaaAdbInputMethodEnum.AdbShell,
                    config={},
                )
                job = controller.post_connection()
                job.wait()
                if not job.succeeded:
                    raise ConnectionError(f"连接失败: {cfg.adb_address}")
                logger.info(f"已连接所选ADB设备: {cfg.adb_address}")
                return device
            except Exception as e:
                logger.warning(
                    f"所选设备 {cfg.adb_address} 连接失败: {e},等待设备上线..."
                )
        return self._wait_device_polling()

    def _build_selected_device(self):
        from maa.define import MaaAdbScreencapMethodEnum
        from maa.toolkit import AdbDevice

        return AdbDevice(
            name=cfg.adb_address,
            adb_path=cfg.adb_dir,
            address=cfg.adb_address,
            screencap_methods=MaaAdbScreencapMethodEnum.All,
            input_methods=MaaAdbInputMethodEnum.AdbShell,
            config={},
        )

    def _wait_device_polling(self):
        """轮询查找ADB设备:先连接模拟器端口,再尝试自动检测,必要时重启ADB,可被停止操作取消"""
        logger.info("尝试寻找ADB设备")
        start_server()
        connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)
        attempt = 0
        while True:
            attempt += 1
            devices = self._find_devices()
            if cfg.adb_address:
                for device in devices:
                    if device.address == cfg.adb_address:
                        return device
                if attempt == 1 or attempt % 5 == 0:
                    connect_adb_devices([cfg.adb_address])
                if attempt == 1 or attempt % 5 == 0:
                    logger.info(
                        f"等待指定ADB设备 {cfg.adb_address} 上线,已尝试{attempt}次..."
                    )
            elif devices:
                return devices[0]
            else:
                if attempt == 1 or attempt % 5 == 0:
                    connect_adb_devices()
                if attempt == 1:
                    logger.info("未找到ADB设备,请确认模拟器已启动...")
                elif attempt % 5 == 0:
                    logger.info(f"已尝试{attempt}次,重启ADB服务器...")
                    restart()
                    connect_adb_devices(
                        [cfg.adb_address] if cfg.adb_address else None
                    )
            if not STOP.empty():
                raise StopException("取消等待ADB设备")
            time.sleep(2)

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
    """返回当前已连接的ADB设备列表"""
    try:
        Toolkit.init_option(cfg.tool_kit_option)
        connect_adb_devices([cfg.adb_address] if cfg.adb_address else None)
        return (
            Toolkit.find_adb_devices()
            or Toolkit.find_adb_devices(cfg.adb_dir)
            or []
        )
    except Exception as e:
        logger.warning(f"查找ADB设备失败: {e}")
        return []
