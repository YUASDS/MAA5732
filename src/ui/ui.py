# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'maa-5732.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(680, 580)
        icon = QIcon()
        icon.addFile("assets/resource/image/logo.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.working = QWidget()
        self.working.setObjectName("working")
        self.verticalLayout_2 = QVBoxLayout(self.working)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.SelectBox = QGroupBox(self.working)
        self.SelectBox.setObjectName("SelectBox")
        self.verticalLayout = QVBoxLayout(self.SelectBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.StartToHomeActioncheckBox = QCheckBox(self.SelectBox)
        self.StartToHomeActioncheckBox.setObjectName("StartToHomeActioncheckBox")
        self.StartToHomeActioncheckBox.setChecked(True)

        self.horizontalLayout.addWidget(self.StartToHomeActioncheckBox)

        self.StartButton = QPushButton(self.SelectBox)
        self.StartButton.setObjectName("StartButton")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.StartButton.setIcon(icon1)
        self.StartButton.setCheckable(False)
        self.StartButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.StartButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.GuildcheckBox = QCheckBox(self.SelectBox)
        self.GuildcheckBox.setObjectName("GuildcheckBox")
        self.GuildcheckBox.setChecked(True)

        self.horizontalLayout_3.addWidget(self.GuildcheckBox)

        self.GuildButton = QPushButton(self.SelectBox)
        self.GuildButton.setObjectName("GuildButton")
        self.GuildButton.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.GuildButton)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.GetMailcheckBox = QCheckBox(self.SelectBox)
        self.GetMailcheckBox.setObjectName("GetMailcheckBox")
        self.GetMailcheckBox.setChecked(True)

        self.horizontalLayout_17.addWidget(self.GetMailcheckBox)

        self.verticalLayout.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.PurchasecheckBox = QCheckBox(self.SelectBox)
        self.PurchasecheckBox.setObjectName("PurchasecheckBox")
        self.PurchasecheckBox.setChecked(True)

        self.horizontalLayout_4.addWidget(self.PurchasecheckBox)

        self.PurchaseButton = QPushButton(self.SelectBox)
        self.PurchaseButton.setObjectName("PurchaseButton")
        self.PurchaseButton.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.PurchaseButton)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ConstructioncheckBox = QCheckBox(self.SelectBox)
        self.ConstructioncheckBox.setObjectName("ConstructioncheckBox")
        self.ConstructioncheckBox.setChecked(True)

        self.horizontalLayout_5.addWidget(self.ConstructioncheckBox)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.BureaucheckBox = QCheckBox(self.SelectBox)
        self.BureaucheckBox.setObjectName("BureaucheckBox")
        self.BureaucheckBox.setChecked(True)

        self.horizontalLayout_6.addWidget(self.BureaucheckBox)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.FriendscheckBox = QCheckBox(self.SelectBox)
        self.FriendscheckBox.setObjectName("FriendscheckBox")
        self.FriendscheckBox.setChecked(True)

        self.horizontalLayout_7.addWidget(self.FriendscheckBox)

        self.FriendsButton = QPushButton(self.SelectBox)
        self.FriendsButton.setObjectName("FriendsButton")
        self.FriendsButton.setIcon(icon1)

        self.horizontalLayout_7.addWidget(self.FriendsButton)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.RaidcheckBox = QCheckBox(self.SelectBox)
        self.RaidcheckBox.setObjectName("RaidcheckBox")
        self.RaidcheckBox.setChecked(True)

        self.horizontalLayout_9.addWidget(self.RaidcheckBox)

        self.RaidButton = QPushButton(self.SelectBox)
        self.RaidButton.setObjectName("RaidButton")
        self.RaidButton.setIcon(icon1)

        self.horizontalLayout_9.addWidget(self.RaidButton)

        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.SupervisioncheckBox = QCheckBox(self.SelectBox)
        self.SupervisioncheckBox.setObjectName("SupervisioncheckBox")
        self.SupervisioncheckBox.setChecked(True)

        self.horizontalLayout_10.addWidget(self.SupervisioncheckBox)

        self.SupervisionButton = QPushButton(self.SelectBox)
        self.SupervisionButton.setObjectName("SupervisionButton")
        self.SupervisionButton.setIcon(icon1)

        self.horizontalLayout_10.addWidget(self.SupervisionButton)

        self.verticalLayout.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.SlectAllButton = QPushButton(self.SelectBox)
        self.SlectAllButton.setObjectName("SlectAllButton")

        self.horizontalLayout_12.addWidget(self.SlectAllButton)

        self.ClearAllButton = QPushButton(self.SelectBox)
        self.ClearAllButton.setObjectName("ClearAllButton")

        self.horizontalLayout_12.addWidget(self.ClearAllButton)

        self.verticalLayout.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_8.addWidget(self.SelectBox)

        self.SettingBox = QGroupBox(self.working)
        self.SettingBox.setObjectName("SettingBox")
        self.horizontalLayout_14 = QHBoxLayout(self.SettingBox)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.stackedWidget = QStackedWidget(self.SettingBox)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.StartToHomeAction = QWidget()
        self.StartToHomeAction.setObjectName("StartToHomeAction")
        self.StartToHomeAction.setEnabled(True)
        self.StartToHomeAction.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.StartToHomeAction.setContextMenuPolicy(
            Qt.ContextMenuPolicy.ActionsContextMenu
        )
        self.verticalLayout_12 = QVBoxLayout(self.StartToHomeAction)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.StartToHomeAction_StartAPPcheckBox = QCheckBox(self.StartToHomeAction)
        self.StartToHomeAction_StartAPPcheckBox.setObjectName(
            "StartToHomeAction_StartAPPcheckBox"
        )
        self.StartToHomeAction_StartAPPcheckBox.setCheckable(True)
        self.StartToHomeAction_StartAPPcheckBox.setChecked(False)

        self.verticalLayout_12.addWidget(self.StartToHomeAction_StartAPPcheckBox)

        self.StartToHomeAction_ServerCheckcomboBox = QComboBox(self.StartToHomeAction)
        self.StartToHomeAction_ServerCheckcomboBox.setObjectName(
            "StartToHomeAction_ServerCheckcomboBox"
        )
        self.StartToHomeAction_ServerCheckcomboBox.setEnabled(True)
        self.StartToHomeAction_ServerCheckcomboBox.setEditable(False)

        self.verticalLayout_12.addWidget(self.StartToHomeAction_ServerCheckcomboBox)

        self.stackedWidget.addWidget(self.StartToHomeAction)
        self.Guild = QWidget()
        self.Guild.setObjectName("Guild")
        self.verticalLayout_11 = QVBoxLayout(self.Guild)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.Guild_GuildCombo = QComboBox(self.Guild)
        self.Guild_GuildCombo.setObjectName("Guild_GuildCombo")

        self.verticalLayout_11.addWidget(self.Guild_GuildCombo)

        self.stackedWidget.addWidget(self.Guild)
        self.Purchase = QWidget()
        self.Purchase.setObjectName("Purchase")
        self.verticalLayout_10 = QVBoxLayout(self.Purchase)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.Purchase_FriendShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_FriendShopcheckBox.setObjectName("Purchase_FriendShopcheckBox")
        self.Purchase_FriendShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_FriendShopcheckBox)

        self.Purchase_ActivityShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_ActivityShopcheckBox.setObjectName(
            "Purchase_ActivityShopcheckBox"
        )
        self.Purchase_ActivityShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_ActivityShopcheckBox)

        self.Purchase_FreeShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_FreeShopcheckBox.setObjectName("Purchase_FreeShopcheckBox")
        self.Purchase_FreeShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_FreeShopcheckBox)

        self.verticalLayout_10.addLayout(self.verticalLayout_6)

        self.stackedWidget.addWidget(self.Purchase)
        self.Friends = QWidget()
        self.Friends.setObjectName("Friends")
        self.verticalLayout_5 = QVBoxLayout(self.Friends)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Friends_FriendPointcheckBox = QCheckBox(self.Friends)
        self.Friends_FriendPointcheckBox.setObjectName("Friends_FriendPointcheckBox")
        self.Friends_FriendPointcheckBox.setChecked(True)

        self.verticalLayout_4.addWidget(self.Friends_FriendPointcheckBox)

        self.Friends_AutoLikecheckBox = QCheckBox(self.Friends)
        self.Friends_AutoLikecheckBox.setObjectName("Friends_AutoLikecheckBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.Friends_AutoLikecheckBox.sizePolicy().hasHeightForWidth()
        )
        self.Friends_AutoLikecheckBox.setSizePolicy(sizePolicy)
        self.Friends_AutoLikecheckBox.setChecked(True)

        self.verticalLayout_4.addWidget(self.Friends_AutoLikecheckBox)

        self.verticalLayout_4.setStretch(0, 1)

        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.stackedWidget.addWidget(self.Friends)
        self.Raid = QWidget()
        self.Raid.setObjectName("Raid")
        self.verticalLayout_9 = QVBoxLayout(self.Raid)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.Raid_RaidDarkcheckBox = QCheckBox(self.Raid)
        self.Raid_RaidDarkcheckBox.setObjectName("Raid_RaidDarkcheckBox")
        self.Raid_RaidDarkcheckBox.setChecked(True)

        self.verticalLayout_7.addWidget(self.Raid_RaidDarkcheckBox)

        self.Raid_RaidRivercheckBox = QCheckBox(self.Raid)
        self.Raid_RaidRivercheckBox.setObjectName("Raid_RaidRivercheckBox")
        self.Raid_RaidRivercheckBox.setChecked(True)

        self.verticalLayout_7.addWidget(self.Raid_RaidRivercheckBox)

        self.Raid_StromLevelCombo = QComboBox(self.Raid)
        self.Raid_StromLevelCombo.setObjectName("Raid_StromLevelCombo")

        self.verticalLayout_7.addWidget(self.Raid_StromLevelCombo)

        self.Raid_RaidFightcheckBox = QCheckBox(self.Raid)
        self.Raid_RaidFightcheckBox.setObjectName("Raid_RaidFightcheckBox")

        self.verticalLayout_7.addWidget(self.Raid_RaidFightcheckBox)

        self.Raid_ResourceCombo = QComboBox(self.Raid)
        self.Raid_ResourceCombo.setObjectName("Raid_ResourceCombo")

        self.verticalLayout_7.addWidget(self.Raid_ResourceCombo)

        self.Raid_ResourceLevelCombo = QComboBox(self.Raid)
        self.Raid_ResourceLevelCombo.setObjectName("Raid_ResourceLevelCombo")

        self.verticalLayout_7.addWidget(self.Raid_ResourceLevelCombo)

        self.verticalLayout_9.addLayout(self.verticalLayout_7)

        self.stackedWidget.addWidget(self.Raid)
        self.Supervision = QWidget()
        self.Supervision.setObjectName("Supervision")
        self.verticalLayout_8 = QVBoxLayout(self.Supervision)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.Supervision_RewardCombo = QComboBox(self.Supervision)
        self.Supervision_RewardCombo.setObjectName("Supervision_RewardCombo")

        self.verticalLayout_8.addWidget(self.Supervision_RewardCombo)

        self.stackedWidget.addWidget(self.Supervision)
        self.RestPage_2 = QWidget()
        self.RestPage_2.setObjectName("RestPage_2")
        self.stackedWidget.addWidget(self.RestPage_2)
        self.RestPage_1 = QWidget()
        self.RestPage_1.setObjectName("RestPage_1")
        self.stackedWidget.addWidget(self.RestPage_1)

        self.horizontalLayout_14.addWidget(self.stackedWidget)

        self.horizontalLayout_8.addWidget(self.SettingBox)

        self.LogBox = QGroupBox(self.working)
        self.LogBox.setObjectName("LogBox")
        self.horizontalLayout_11 = QHBoxLayout(self.LogBox)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.textBrowser = QTextBrowser(self.LogBox)
        self.textBrowser.setObjectName("textBrowser")

        self.horizontalLayout_11.addWidget(self.textBrowser)

        self.horizontalLayout_8.addWidget(self.LogBox)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 1)
        self.horizontalLayout_8.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.LinkStartButton = QPushButton(self.working)
        self.LinkStartButton.setObjectName("LinkStartButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.LinkStartButton.sizePolicy().hasHeightForWidth()
        )
        self.LinkStartButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_15.addWidget(self.LinkStartButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_15)

        self.tabWidget.addTab(self.working, "")
        self.tools = QWidget()
        self.tools.setObjectName("tools")
        self.tabWidget.addTab(self.tools, "")
        self.settings = QWidget()
        self.settings.setObjectName("settings")
        self.settings.setMouseTracking(False)
        self.verticalLayout_13 = QVBoxLayout(self.settings)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.UpdateBox = QGroupBox(self.settings)
        self.UpdateBox.setObjectName("UpdateBox")
        self.horizontalLayout_16 = QHBoxLayout(self.UpdateBox)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.CheckUpdatecheckBox = QCheckBox(self.UpdateBox)
        self.CheckUpdatecheckBox.setObjectName("CheckUpdatecheckBox")
        self.CheckUpdatecheckBox.setChecked(True)

        self.horizontalLayout_16.addWidget(self.CheckUpdatecheckBox)

        self.CheckUpdateButton = QPushButton(self.UpdateBox)
        self.CheckUpdateButton.setObjectName("CheckUpdateButton")

        self.horizontalLayout_16.addWidget(self.CheckUpdateButton)

        self.verticalLayout_13.addWidget(self.UpdateBox)

        self.GameBox = QGroupBox(self.settings)
        self.GameBox.setObjectName("GameBox")
        self.verticalLayout_14 = QVBoxLayout(self.GameBox)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.GamePathLabel = QLabel(self.GameBox)
        self.GamePathLabel.setObjectName("GamePathLabel")

        self.horizontalLayout_18.addWidget(self.GamePathLabel)

        self.GamePathEdit = QLineEdit(self.GameBox)
        self.GamePathEdit.setObjectName("GamePathEdit")

        self.horizontalLayout_18.addWidget(self.GamePathEdit)

        self.BrowseButton = QPushButton(self.GameBox)
        self.BrowseButton.setObjectName("BrowseButton")

        self.horizontalLayout_18.addWidget(self.BrowseButton)

        self.verticalLayout_14.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.GameArgsLabel = QLabel(self.GameBox)
        self.GameArgsLabel.setObjectName("GameArgsLabel")

        self.horizontalLayout_19.addWidget(self.GameArgsLabel)

        self.GameArgsEdit = QLineEdit(self.GameBox)
        self.GameArgsEdit.setObjectName("GameArgsEdit")

        self.horizontalLayout_19.addWidget(self.GameArgsEdit)

        self.verticalLayout_14.addLayout(self.horizontalLayout_19)

        self.verticalLayout_13.addWidget(self.GameBox)

        self.DeviceBox = QGroupBox(self.settings)
        self.DeviceBox.setObjectName("DeviceBox")
        self.horizontalLayout_21 = QHBoxLayout(self.DeviceBox)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.DeviceLabel = QLabel(self.DeviceBox)
        self.DeviceLabel.setObjectName("DeviceLabel")

        self.horizontalLayout_21.addWidget(self.DeviceLabel)

        self.DeviceCombo = QComboBox(self.DeviceBox)
        self.DeviceCombo.setObjectName("DeviceCombo")

        self.horizontalLayout_21.addWidget(self.DeviceCombo)

        self.DeviceRefreshButton = QPushButton(self.DeviceBox)
        self.DeviceRefreshButton.setObjectName("DeviceRefreshButton")

        self.horizontalLayout_21.addWidget(self.DeviceRefreshButton)

        self.verticalLayout_13.addWidget(self.DeviceBox)

        self.RunBox = QGroupBox(self.settings)
        self.RunBox.setObjectName("RunBox")
        self.verticalLayout_15 = QVBoxLayout(self.RunBox)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.AutoRuncheckBox = QCheckBox(self.RunBox)
        self.AutoRuncheckBox.setObjectName("AutoRuncheckBox")

        self.verticalLayout_15.addWidget(self.AutoRuncheckBox)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.AfterFinishLabel = QLabel(self.RunBox)
        self.AfterFinishLabel.setObjectName("AfterFinishLabel")

        self.horizontalLayout_20.addWidget(self.AfterFinishLabel)

        self.AfterFinishCombo = QComboBox(self.RunBox)
        self.AfterFinishCombo.setObjectName("AfterFinishCombo")

        self.horizontalLayout_20.addWidget(self.AfterFinishCombo)

        self.verticalLayout_15.addLayout(self.horizontalLayout_20)

        self.verticalLayout_13.addWidget(self.RunBox)

        self.tabWidget.addTab(self.settings, "")

        self.verticalLayout_3.addWidget(self.tabWidget)

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(4)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Maa5732", None))
        self.SelectBox.setTitle("")
        self.StartToHomeActioncheckBox.setText(
            QCoreApplication.translate("Form", "\u542f\u52a8", None)
        )
        self.StartButton.setText("")
        self.GuildcheckBox.setText(
            QCoreApplication.translate("Form", "\u5de5\u4f1a\u6350\u8d60", None)
        )
        self.GuildButton.setText("")
        self.GetMailcheckBox.setText(
            QCoreApplication.translate("Form", "\u90ae\u4ef6\u9886\u53d6", None)
        )
        self.PurchasecheckBox.setText(
            QCoreApplication.translate("Form", "\u91c7\u8d2d\u4e2d\u5fc3", None)
        )
        self.PurchaseButton.setText("")
        self.ConstructioncheckBox.setText(
            QCoreApplication.translate("Form", "\u57fa\u5efa\u6536\u83dc", None)
        )
        self.BureaucheckBox.setText(
            QCoreApplication.translate("Form", "\u7ba1\u7406\u5c40", None)
        )
        self.FriendscheckBox.setText(
            QCoreApplication.translate("Form", "\u597d\u53cb", None)
        )
        self.FriendsButton.setText("")
        self.RaidcheckBox.setText(
            QCoreApplication.translate("Form", "\u526f\u672c", None)
        )
        self.RaidButton.setText("")
        self.SupervisioncheckBox.setText(
            QCoreApplication.translate("Form", "\u76d1\u5bdf\u5bc6\u4ee4", None)
        )
        self.SupervisionButton.setText("")
        self.SlectAllButton.setText(
            QCoreApplication.translate("Form", "\u5168\u9009", None)
        )
        self.ClearAllButton.setText(
            QCoreApplication.translate("Form", "\u6e05\u7a7a", None)
        )
        self.SettingBox.setTitle("")
        self.StartToHomeAction_StartAPPcheckBox.setText(
            QCoreApplication.translate("Form", "\u542f\u52a8\u6e38\u620f", None)
        )
        self.Purchase_FriendShopcheckBox.setText(
            QCoreApplication.translate("Form", "\u53cb\u60c5\u70b9\u5546\u5e97", None)
        )
        self.Purchase_ActivityShopcheckBox.setText(
            QCoreApplication.translate("Form", "\u6d3b\u52a8\u5546\u5e97", None)
        )
        self.Purchase_FreeShopcheckBox.setText(
            QCoreApplication.translate("Form", "\u514d\u8d39\u4f53\u529b", None)
        )
        self.Friends_FriendPointcheckBox.setText(
            QCoreApplication.translate(
                "Form", "\u6536\u53d6\u8d60\u9001\u53cb\u60c5\u70b9", None
            )
        )
        self.Friends_AutoLikecheckBox.setText(
            QCoreApplication.translate("Form", "\u81ea\u52a8\u70b9\u8d5e", None)
        )
        self.Raid_RaidDarkcheckBox.setText(
            QCoreApplication.translate("Form", "\u6df1\u4e95", None)
        )
        self.Raid_RaidRivercheckBox.setText(
            QCoreApplication.translate("Form", "\u8bb0\u5fc6\u98ce\u66b4", None)
        )
        self.Raid_RaidFightcheckBox.setText(
            QCoreApplication.translate("Form", "\u4f53\u529b\u526f\u672c", None)
        )
        self.LogBox.setTitle("")
        self.LinkStartButton.setText(
            QCoreApplication.translate("Form", "Link Start\uff01", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.working),
            QCoreApplication.translate("Form", "\u4e00\u952e\u957f\u8349", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tools),
            QCoreApplication.translate("Form", "\u5de5\u5177", None),
        )
        # if QT_CONFIG(accessibility)
        self.settings.setAccessibleName("")
        # endif // QT_CONFIG(accessibility)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.settings),
            QCoreApplication.translate("Form", "\u8bbe\u7f6e", None),
        )
        self.UpdateBox.setTitle(
            QCoreApplication.translate("Form", "\u66f4\u65b0\u68c0\u6d4b", None)
        )
        self.CheckUpdatecheckBox.setText(
            QCoreApplication.translate("Form", "\u542f\u52a8\u65f6\u68c0\u67e5\u66f4\u65b0", None)
        )
        self.CheckUpdateButton.setText(
            QCoreApplication.translate("Form", "\u68c0\u67e5\u66f4\u65b0", None)
        )
        self.GameBox.setTitle(
            QCoreApplication.translate("Form", "\u6e38\u620f\u8bbe\u7f6e", None)
        )
        self.GamePathLabel.setText(
            QCoreApplication.translate("Form", "\u6e38\u620f\u5730\u5740", None)
        )
        self.GamePathEdit.setPlaceholderText(
            QCoreApplication.translate(
                "Form", "\u6a21\u62df\u5668\u6216\u6e38\u620fexe\u8def\u5f84,\u7559\u7a7a\u5219\u4f7f\u7528ADB\u542f\u52a8", None
            )
        )
        self.BrowseButton.setText(
            QCoreApplication.translate("Form", "\u6d4f\u89c8...", None)
        )
        self.GameArgsLabel.setText(
            QCoreApplication.translate("Form", "\u9644\u52a0\u53c2\u6570", None)
        )
        self.GameArgsEdit.setPlaceholderText(
            QCoreApplication.translate(
                "Form", "\u542f\u52a8\u53c2\u6570,\u4ee5\u7a7a\u683c\u5206\u9694", None
            )
        )
        self.RunBox.setTitle(
            QCoreApplication.translate("Form", "\u8fd0\u884c\u8bbe\u7f6e", None)
        )
        self.AutoRuncheckBox.setText(
            QCoreApplication.translate("Form", "\u542f\u52a8\u540e\u81ea\u52a8\u8fd0\u884c", None)
        )
        self.AfterFinishLabel.setText(
            QCoreApplication.translate("Form", "\u7ed3\u675f\u540e\u884c\u4e3a", None)
        )
        self.DeviceBox.setTitle(
            QCoreApplication.translate("Form", "\u8bbe\u5907\u8bbe\u7f6e", None)
        )
        self.DeviceLabel.setText(
            QCoreApplication.translate("Form", "ADB\u8bbe\u5907", None)
        )
        self.DeviceRefreshButton.setText(
            QCoreApplication.translate("Form", "\u5237\u65b0", None)
        )

    # retranslateUi
