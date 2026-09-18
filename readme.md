# MAA5732

<div><p align="center">
<img src="assets\resource\image\logo.ico" /></p></div>

Base on [MaaFramwork](https://github.com/MaaXYZ/MaaFramework)
部分代码参考了 [MaaYYS](https://github.com/TanyaShue/MaaYYs)图标来源于网络，如有侵权，请联系删除。
<!-- markdownlint-disable MD033 MD041 -->
<div align="center">
<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" /><a href="https://github.com/YUASDS/Maa5732/blob/main/LICENSE"><img src="https://img.shields.io/github/license/YUASDS/Maa5732" alt="Licence" /></a>
<p align="center">
<img src="https://count.getloli.com/get/@YUASDS-Maa5732?theme=rule34" alt="访问次数" /></p></div>

## 计划功能

- [ ] 定时启动游戏
- [x] 完成登录及签到月卡
- [x] 工会捐赠(基本完成)
- [x] 采购办免费体力
- [x] 采购办友情点商店
- [ ] 采购办活动商店
- [x] 邮件领取
- [x] 基建收菜
- [x] 管理局体力
- [x] 定向刷取材料
- [x] 管理局定向派遣
- [x] 赠送/收取友情点
- [ ] 自动点赞
- [x] 深井扫荡
- [x] 锈河扫荡
- [x] 监察密令领取
- [ ] 自动切换扫荡队伍

## 界面

<div style="text-align: left;">
  <img src="assets/resource/image/interface.png" style="width: 50%;" />
</div>
## 使用方法

- 下载Release,解压并运行MAA_5732.exe即可
- 启动功能可直接启动游戏，基本稳定
- 其他功能的需要在游戏主界面开始
- 目前能完成游戏中的大部分日常

## 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

`assets/` 中只有模板图、`assets/ui` 图标等必需资源纳入版本控制，以下资源需要自行准备（Release 压缩包中已包含）：

- `assets/adb/adb.exe`：自带adb，缺失时回退使用系统PATH中的adb
- `assets/resource/model/ocr/`：OCR模型(det.onnx / rec.onnx / keys.txt)
- `assets/MaaCommonAssets/`：可选，MaaFramework公共资源

首次运行会自动生成 `assets/config/config.json`；该文件是运行时配置，不纳入版本控制。

## 日志

- 日志同时写入 `logs/`（保留最近7天）和运行终端
- 终端默认输出 DEBUG ：

```bat
set MAA5732_LOG_LEVEL=DEBUG
MAA_5732_0.2.4.exe
```

## 打包

```bash
python build.py
```

生成的 `MAA_5732_x.y.z.exe` 与 `MAA_5732_x.y.z.zip` 位于 `dist/`。
