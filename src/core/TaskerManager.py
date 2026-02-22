import queue
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
from src.utils.adb import restart
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
        adb_devices = Toolkit.find_adb_devices() or Toolkit.find_adb_devices(
            cfg.adb_dir
        )
        if not adb_devices:
            logger.info("重启ADB ")
            restart()
            adb_devices = Toolkit.find_adb_devices() or Toolkit.find_adb_devices(
                cfg.adb_dir
            )

        device = adb_devices[0]
        self.controller = AdbController(
            adb_path=device.adb_path,
            address=device.address,
            screencap_methods=device.screencap_methods,
            input_methods=MaaAdbInputMethodEnum.AdbShell,
            config={},
            # config=device.config,
        )
        self.controller.post_connection().wait()
        self.tasker = Tasker()
        # self.tasker = Tasker(notification_handler=MyNotificationHandler())
        self.tasker.bind(self.resource, self.controller)
        self._register_custom_action()
        self.init_flag_queue.put(1)
        logger.info("初始化成功!!!")

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

        return warp_action

    def _register_custom_action(self):
        for key, value in self.custon_action.items():
            self.resource.register_custom_action(key, value())  # type: ignore


TASKER_MANAGER = TaskerManager()
