# 导入sys
import sys
import re
import html
import threading
from functools import partial
from typing import Union
from loguru import logger
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import QObject, Signal, QTimer, Qt
from subprocess import run as adb_run, PIPE

from src.ui.ui import Ui_Form
from src.ui.theme import apply_theme
from src.ui.title_bar import TitleBar
from src.ui.update_dialog import UpdateDialog
from src.utils.configs import cfg, save_confg
from src.utils.updater import check_update, is_newer
from src.utils.adb import close_emulator
from src.utils.click import start_by_exe
from src.core import version
from src.core.ThreadManager import TaskerThread
from src.core.TaskerManager import list_adb_devices


class MySignal(QObject):
    button = Signal(QPushButton, str)
    finish = Signal(str)
    update = Signal(object, object, object, bool)
    devices = Signal(list, list)


class LogSignals(QObject):
    log_message = Signal(str, str)


# 去除ANSI颜色代码的辅助函数
def remove_ansi_codes(text):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# 自定义日志处理器函数
def log_to_textbrowser(message, signals):
    """处理日志消息并发送到TextBrowser"""
    cleaned_message = remove_ansi_codes(message.record["message"])
    signals.log_message.emit(message.record["level"].name, cleaned_message)


# 继承QWidget类,以获取其属性和方法
class MyWidget(QWidget):
    order = {}
    state = 0
    widget_button: list[QPushButton] = []
    check_box_dict: dict[str, QCheckBox] = {}
    detail_dict: dict[str, dict[str, Union[QCheckBox, QComboBox]]] = {}

    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.tasker_thread = TaskerThread(self.change_running_state, self.finish_callback)
        self.tasker_thread.daemon = True
        self.tasker_thread.start()
        self.signal = MySignal()
        self.signal.button.connect(self.print_gui)
        self.signal.finish.connect(self.on_finish)
        self.signal.update.connect(self.on_update_result)
        self.signal.devices.connect(self.on_devices)

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.title_bar = TitleBar(self)
        self.ui.verticalLayout_3.insertWidget(0, self.title_bar)

        self.text_browser = self.ui.textBrowser
        # 创建日志信号对象
        self.log_signals = LogSignals()
        # 连接信号到文本追加槽
        self.log_signals.log_message.connect(self.append_log)

        # 配置loguru
        self.setup_logger()
        # 为按钮添加点击事件 用于切换界面
        self.widget_button.append(self.ui.GuildButton)
        self.widget_button.append(self.ui.RaidButton)
        self.widget_button.append(self.ui.StartButton)
        self.widget_button.append(self.ui.FriendsButton)
        self.widget_button.append(self.ui.PurchaseButton)
        self.widget_button.append(self.ui.SupervisionButton)

        for button in self.widget_button:
            button.clicked.connect(self.buttonClick)
        self.ui.LinkStartButton.clicked.connect(self.start)
        self.ui.SlectAllButton.clicked.connect(self.select_all)
        self.ui.ClearAllButton.clicked.connect(self.clear_all)
        # nothing 不进行注册
        # 对于checkBox进行注册 用于是否进行该项任务
        self.add_check_box(self.ui.GuildcheckBox)
        self.add_check_box(self.ui.RaidcheckBox)
        self.add_check_box(self.ui.StartToHomeActioncheckBox)
        self.add_check_box(self.ui.FriendscheckBox)
        self.add_check_box(self.ui.PurchasecheckBox)
        self.add_check_box(self.ui.SupervisioncheckBox)
        self.add_check_box(self.ui.ConstructioncheckBox)
        self.add_check_box(self.ui.BureaucheckBox)
        self.add_check_box(self.ui.GetMailcheckBox)

        # 对每项任务的详细设置进行注册 格式为 任务名_设置名
        self.add_detail_box(self.ui.Purchase_ActivityShopcheckBox)
        self.add_detail_box(self.ui.Purchase_FreeShopcheckBox)
        self.add_detail_box(self.ui.Purchase_FriendShopcheckBox)
        self.add_detail_box(self.ui.Friends_AutoLikecheckBox)
        self.add_detail_box(self.ui.Friends_FriendPointcheckBox)
        self.add_detail_box(self.ui.Raid_RaidDarkcheckBox)
        self.add_detail_box(self.ui.Raid_RaidFightcheckBox)
        self.add_detail_box(self.ui.Raid_RaidRivercheckBox)

        self.add_detail_box(self.ui.Guild_GuildCombo)
        self.add_detail_box(self.ui.Raid_ResourceCombo)
        self.add_detail_box(self.ui.Raid_ResourceLevelCombo)
        self.add_detail_box(self.ui.Raid_StromLevelCombo)
        self.add_detail_box(self.ui.Supervision_RewardCombo)
        self.add_detail_box(self.ui.StartToHomeAction_ServerCheckcomboBox)
        self.add_detail_box(self.ui.StartToHomeAction_StartAPPcheckBox)
        self.init_combo()
        self.load_from_json(cfg.settings)
        self.init_settings()

    def setup_logger(self):
        """配置loguru使用自定义处理器"""
        # 添加自定义处理器（使用partial绑定信号对象）
        logger.add(level="INFO",
            sink=partial(log_to_textbrowser, signals=self.log_signals),
            format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            colorize=True,  # 允许在终端保留颜色
        )

    def append_log(self, level, message):
        """支持HTML格式的彩色日志"""
        color_map = {
            "ERROR": "#E85D75",
            "WARNING": "#E8A33D",
            "INFO": "#43D9B5",
            "DEBUG": "#7A86A0",
            "TRACE": "#6E7A94",
        }
        color = color_map.get(level, "#E6E9F0")
        self.text_browser.append(
            f'<span style="color:{color}">{html.escape(message)}</span>'
        )

    def add_check_box(self, check_box: QCheckBox):
        check_box.clicked.connect(self.checkBox)
        self.check_box_dict[check_box.objectName().replace("checkBox", "")] = check_box

    def add_detail_box(self, obj: Union[QCheckBox, QComboBox]):
        action_name = obj.objectName().split("_")[0]
        action_setting = obj.objectName().split("_")[1]
        if action_name not in self.detail_dict:
            self.detail_dict[action_name] = {}
        self.detail_dict[action_name][action_setting] = obj

    def init_combo(self):
        # 为下拉框添加选项
        self.ui.StartToHomeAction_ServerCheckcomboBox.addItems(["B服", "官服"])
        self.ui.Guild_GuildCombo.addItems(["狄斯币", "异方晶"])
        self.ui.Raid_ResourceCombo.addItems(
            [
                "狄斯币",
                "狂乱精粹",
                "技能模组",
                "重构碎片",
                "异能源质",
                "诡秘源质",
                "坚韧源质",
                "狂暴源质",
                "精准源质",
                "启迪源质",
            ]
        )
        self.ui.Raid_ResourceLevelCombo.addItems(["1", "2", "3", "4", "5"])
        self.ui.Raid_StromLevelCombo.addItems(["1", "2", "3", "4", "5"])
        self.ui.Supervision_RewardCombo.addItems(["体力", "监察徽印"])

    def checkBox(self):
        box = self.sender()
        boxName = box.objectName()

    def select_all(self):
        for checkBox in self.check_box_dict.values():
            checkBox.setChecked(True)

    def clear_all(self):
        for checkBox in self.check_box_dict.values():
            checkBox.setChecked(False)

    def buttonClick(self):
        self.state_to_json()
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == "RaidButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Raid)
        if btnName == "GuildButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Guild)
        if btnName == "StartButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.StartToHomeAction)
        if btnName == "FriendsButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Friends)
        if btnName == "PurchaseButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Purchase)
        if btnName == "SupervisionButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)
        if btnName == "SlectAllButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)
        if btnName == "ClearAllButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)

    def print_gui(self, obj: QObject, msg: str):
        if isinstance(obj, QPushButton):
            obj.setText(msg)

    def change_running_state(self):
        if self.state == 0:
            self.signal.button.emit(self.ui.LinkStartButton, "Stop")
            self.ui.LinkStartButton.setProperty("running", True)
            self.state = 1
        else:
            self.signal.button.emit(self.ui.LinkStartButton, "Link Start ! ")
            self.ui.LinkStartButton.setProperty("running", False)
            self.state = 0
        self.ui.LinkStartButton.style().unpolish(self.ui.LinkStartButton)
        self.ui.LinkStartButton.style().polish(self.ui.LinkStartButton)

    def start(self):
        if self.state == 0:
            self.change_running_state()
            json_data = self.state_to_json()
            self.tasker_thread.add_task(self.state_to_json())
            cfg.settings = json_data
            save_confg()
        else:
            # self.change_running_state()
            self.tasker_thread.cancle_task()

    def load_from_json(self, data: list[dict]):
        for key, value in data[0].items():
            self.check_box_dict[key].setChecked(value)
        for key, value in data[1].items():
            if key in self.detail_dict:
                for inner_key, inner_value in value.items():
                    if inner_key in self.detail_dict[key]:
                        qobj = self.detail_dict[key][inner_key]
                        if isinstance(qobj, QCheckBox):
                            qobj.setChecked(inner_value)
                        else:
                            qobj.setCurrentText(inner_value)

    def state_to_json(self):
        detail_part = {key: {} for key in self.detail_dict.keys()}
        first_part = {
            name: obj.isChecked() for name, obj in self.check_box_dict.items()
        }
        for key, value in self.detail_dict.items():
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, QCheckBox):
                    detail_part[key][inner_key] = inner_value.isChecked()
                else:
                    detail_part[key][inner_key] = inner_value.currentText()
        return [first_part, detail_part]

    def init_settings(self):
        self.ui.AfterFinishCombo.addItems(
            ["无", "关闭软件", "关闭模拟器", "关闭软件和关闭模拟器"]
        )
        self.ui.CheckUpdatecheckBox.setChecked(cfg.check_update)
        self.ui.AutoRuncheckBox.setChecked(cfg.auto_run)
        self.ui.GamePathEdit.setText(cfg.game_path)
        self.ui.GameArgsEdit.setText(cfg.game_args)
        self.ui.AfterFinishCombo.setCurrentText(cfg.after_finish)

        self.ui.CheckUpdateButton.clicked.connect(
            lambda: self.check_update(manual=True)
        )
        self.ui.BrowseButton.clicked.connect(self.browse_game)
        self.ui.CheckUpdatecheckBox.toggled.connect(self.save_settings)
        self.ui.AutoRuncheckBox.toggled.connect(self.save_settings)
        self.ui.GamePathEdit.textEdited.connect(self.save_settings)
        self.ui.GameArgsEdit.textEdited.connect(self.save_settings)
        self.ui.AfterFinishCombo.currentTextChanged.connect(self.save_settings)
        self.ui.DeviceRefreshButton.clicked.connect(self.refresh_devices)
        self.ui.DeviceCombo.currentIndexChanged.connect(self.save_device)
        self.ui.DeviceCombo.setToolTip("选择要使用的ADB设备,可点击刷新获取最新列表")
        QTimer.singleShot(1200, self.refresh_devices)

        if cfg.auto_run:
            QTimer.singleShot(1500, self.auto_start)
        if cfg.check_update:
            QTimer.singleShot(3000, self.check_update)

    def refresh_devices(self):
        if getattr(self, "_refreshing", False):
            return
        self._refreshing = True
        threading.Thread(
            target=self._refresh_devices_worker, daemon=True
        ).start()

    def _refresh_devices_worker(self):
        try:
            all_names = []
            all_addresses = []
            for device in list_adb_devices():
                name = device.name if device.name else device.address
                if "/" in name or "\\" in name:
                    name = device.address
                all_names.append(name)
                all_addresses.append(device.address)
            seen = {}
            names = []
            addresses = []
            for name, address in zip(all_names, all_addresses):
                key = self._device_key(address)
                if key in seen:
                    continue
                seen[key] = True
                names.append(name)
                addresses.append(address)
            connected_ports = {
                a.split(":")[1]
                for a in all_addresses
                if a.startswith("127.0.0.1:")
            }
            filtered = []
            for name, address in zip(names, addresses):
                if address.startswith("emulator-"):
                    port = int(address[len("emulator-"):])
                    if str(port + 1) in connected_ports:
                        continue
                filtered.append((name, address))
            names = [n for n, _ in filtered]
            addresses = [a for _, a in filtered]
            self.signal.devices.emit(names, addresses)
        finally:
            self._refreshing = False

    def _device_key(self, address):
        """通过设备型号识别是否为同一设备,查询失败则用地址本身"""
        try:
            result = adb_run(
                [cfg.adb_dir, "-s", address, "shell", "getprop", "ro.product.model"],
                stdout=PIPE,
                stderr=PIPE,
                timeout=8,
            )
            model = result.stdout.decode(errors="ignore").strip()
            if model:
                return model
        except Exception:
            pass
        return address

    def on_devices(self, names: list, addresses: list):
        combo = self.ui.DeviceCombo
        combo.blockSignals(True)
        combo.clear()
        for name, address in zip(names, addresses):
            text = f"{name} [{address}]" if name != address else address
            combo.addItem(text, address)
        if cfg.adb_address:
            index = combo.findData(cfg.adb_address)
            if index >= 0:
                combo.setCurrentIndex(index)
            elif not self._is_alias(cfg.adb_address, addresses):
                combo.addItem(cfg.adb_address, cfg.adb_address)
                combo.setCurrentIndex(combo.count() - 1)
        elif combo.count() > 0:
            combo.setCurrentIndex(0)
        combo.blockSignals(False)
        logger.debug(f"ADB设备列表已刷新: {combo.count()} 个")

    def _is_alias(self, address, connected):
        """判断emulator-*地址是否为已连接端口的别名"""
        if not address.startswith("emulator-"):
            return False
        try:
            port = int(address[len("emulator-"):])
        except ValueError:
            return False
        return f"127.0.0.1:{port + 1}" in connected

    def save_device(self):
        cfg.adb_address = self.ui.DeviceCombo.currentData() or ""
        save_confg()
        logger.info(f"已选择ADB设备: {cfg.adb_address}")

    def auto_start(self):
        if (
            cfg.game_path
            and self.ui.StartToHomeAction_StartAPPcheckBox.isChecked()
        ):
            logger.info("自动运行: 按设置的游戏地址启动游戏")
            start_by_exe()
        self.start()

    def browse_game(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择游戏或模拟器程序", "", "可执行文件 (*.exe);;所有文件 (*)"
        )
        if path:
            self.ui.GamePathEdit.setText(path)
            cfg.game_path = path
            save_confg()
            logger.info(f"游戏地址已设置: {path}")

    def save_settings(self):
        cfg.check_update = self.ui.CheckUpdatecheckBox.isChecked()
        cfg.auto_run = self.ui.AutoRuncheckBox.isChecked()
        cfg.game_path = self.ui.GamePathEdit.text()
        cfg.game_args = self.ui.GameArgsEdit.text()
        cfg.after_finish = self.ui.AfterFinishCombo.currentText()
        save_confg()

    def finish_callback(self):
        self.signal.finish.emit(cfg.after_finish)

    def on_finish(self, after_finish: str):
        if "关闭模拟器" in after_finish:
            close_emulator()
        if after_finish in ("关闭软件", "关闭软件和关闭模拟器"):
            logger.info("任务结束,关闭软件")
            QTimer.singleShot(500, QApplication.quit)

    def check_update(self, manual: bool = False):
        threading.Thread(
            target=self._check_update_worker, args=(manual,), daemon=True
        ).start()

    def _check_update_worker(self, manual: bool):
        latest, url, body = check_update()
        self.signal.update.emit(latest, url, body, manual)

    def on_update_result(self, latest, url, body, manual: bool):
        if latest is None:
            logger.warning("检查更新失败")
            if manual:
                QMessageBox.warning(self, "更新检查", "检查更新失败,请检查网络连接")
            return
        if not is_newer(latest, version):
            logger.info(f"当前已是最新版本 {version}")
            if manual:
                QMessageBox.information(
                    self, "更新检查", f"当前已是最新版本 {version}"
                )
            return
        if not manual and cfg.dismissed_update == latest:
            logger.info(f"已忽略版本 {latest} 的更新提醒")
            return
        dialog = UpdateDialog(latest, url, body, self)
        dialog.dismissed.connect(lambda: self._dismiss_update(latest))
        dialog.exec()

    def _dismiss_update(self, latest: str):
        cfg.dismissed_update = latest
        save_confg()
        logger.info(f"已忽略版本 {latest} 的更新提醒")


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication,界面展示要包含在QApplication初始化之后,结束之前
    app = QApplication(sys.argv)
    apply_theme(app)
    # 初始化并展示我们的界面组件
    window = MyWidget()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
