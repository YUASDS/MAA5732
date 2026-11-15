# -*- coding: utf-8 -*-
"""材料刷取: 按材料自动刷主线关卡(连续扫荡)

规则与数据见 docs/superpowers/specs/2026-09-12-material-farming-design.md
导航坐标: 已确认的沿用 Raid.py; 主线特有的(旋盘/主线位置/次数区域)需 Task 1 探测后填入,
未就绪时 NAV_READY 保持 False, 任务只记日志不点击。
"""
import json
import re

from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click, stop_sleep
from src.utils.configs import cfg, save_confg
from src.utils.material_data import (
    MAX_CANDIDATES,
    load_material_data,
    plan,
    position_table,
    progress_key,
)
from src.utils.model import StopException

name = __file__.split("\\")[-1].split(".")[0]

# ---------------------------------------------------------------- 导航常量
# 原则: 能用 OCR 文本定位的就不写坐标(游戏改版只换美术时依然可用);
# 只有 OCR 认不出的图标(如次数弹窗的 +)才保留坐标, 并注明原因。
CRISIS_MANAGE_TEXT = "危机管理"        # 主界面底部标签: 确保停在能看到进度卡的界面
CARD_FALLBACK_TEXT = "狄斯"            # 进度卡上的地区名(关卡编号正则没匹配到时的兜底)
STAGE_CODE_RE = r"^[A-Za-z]{0,4}-?N?\d+-[A-Za-z]{0,2}\d+$"   # 关卡编号, 如 N7-1 / ReN7-2 / 13-8 / N3-A1
STAGE_CODE_EXTRA_RE = r"^[A-Za-z]{1,4}-[A-Za-z]{0,2}\d+$"    # 另一套编号(单破折号): Mz-N701 / Sd-1104
# 左侧旋盘上的"主线位置"标签(用于定位可拖动的标签)
REGION_LABELS = ("远邦", "新城·1", "新城", "里湾", "狄斯西区", "狄斯东区")
DIST_CITY = "狄斯城"               # 副本界面底部模式标签; 已在该页时再点无害
# 旋盘(切换主线位置): 按住左侧"主线位置标签"拖动才生效 —— 纯竖直滑动游戏不认,
# 必须带一点 x 漂移; duration 单位是毫秒, 实测 1500 有效(参数经真机验证)。
# 行程实测: 0.08 / 0.11 / 0.134(=标签行距) 都能移动一档, >=0.16 会被游戏忽略(拉过头),
# 因此行程在运行时由 OCR 量出的标签行距推算, 不写死。
DIAL_TRAVEL_RATIO = 0.8            # 行程 = 标签行距 × 该系数
DIAL_TRAVEL_MAX = 0.12             # 行程上限(超过游戏会忽略)
DIAL_TRAVEL_MIN = 0.06
DIAL_TRAVEL_FALLBACK = 0.11        # 量不到标签行距时的行程
DIAL_MS = 1500                     # 拖动时长(毫秒)
DIAL_DRIFT_DOWN = -0.003           # 向下拖时的 x 漂移
DIAL_DRIFT_UP = 0.007              # 向上拖时的 x 漂移
DIAL_FALLBACK = (0.079, 0.50)      # 找不到标签时的兜底起点
DIAL_SETTLE = 2.5                  # 拖动后等待界面稳定
# 旋盘方向约定(真机实测): 向上 = 更新的章节(拖到底是"远邦"一侧),
# 向下 = 更旧的章节(拖到底是狄斯西区 01-08); 与 _detect_progress 的拖向一致。
DIAL_UP = "up"
DIAL_DOWN = "down"
MAX_DIAL_DRAGS = 8                 # 每个方向最多拖几次(主线区域较多)
MAX_DIAL_SCANS = 10                # 探测进度时最多扫几档旋盘
# 地图(副本界面)横向: 一个区域的章节是横向一排(狄斯西区 1-8、里湾 9-13…), 一屏放不下。
# 真机实测一个区域不超过两屏, 所以找章节时不需要算行程与方向, 滑到两端即可覆盖。
MAP_LEFT = "left"                  # 手指向右拖(0.25 -> 0.85): 露出更旧(左)的章节
MAP_RIGHT = "right"                # 手指向左拖(0.85 -> 0.25): 露出更新(右)的章节
MAP_DRAG_BEGIN = 0.25
MAP_DRAG_END = 0.85
MAP_SCAN_STEPS = 4                 # 地图每个方向最多滑几屏
MAP_DETECT_STEPS = 6               # 探测进度时横向滑动的预算(沿用旧实现)
# 横向滑动必须带一点 y 偏移: 纯水平滑动游戏不认(真机实测, 与旋盘必须带 x 漂移同理)。
# 地图与关卡列表各留一个常量便于分别微调, 滑不动时先试改符号/大小(0.006 ≈ 4px)。
MAP_DRAG_DRIFT = -0.006
LIST_DRAG_DRIFT = -0.006
MAP_ROW_Y_FALLBACK = 0.35          # 量不到章节节点 y 时的兜底(probe: 章节节点 y≈0.35)
# 旋盘(主线位置)覆盖的章节 —— 真机 + wiki「主线剧情」页(见 docs/nav_probe/coords.md):
# 狄斯西区(铁血篇) 序章+1-8 / 里湾(锈火篇) 9-13 / 新城-悬城篇 N1-N8 在地图上分两屏
# (新城·1 放 N1-N4、新城 放 N5-N8)、覆海篇 N9-N10 在 远邦。
MAP_REGIONS = (
    ("狄斯西区", (2, 1), (2, 8)),
    ("里湾", (2, 9), (2, 13)),
    ("新城·1", (3, 1), (3, 4)),
    ("新城", (3, 5), (3, 8)),
    ("远邦", (3, 9), (3, 10)),
)
MAX_LIST_SWIPES = 8               # 关卡列表每个方向最多滑动次数(单章最多 18 关)
SWIPE_MS = 800                    # 列表滑动时长基准(毫秒)
# 关卡列表是一整行节点(数字小的在左, 从左到右排布), 整行可能超过一屏:
# 因此滑动前先比较"目标 vs 屏幕上的节点"决定方向, 行程按"序号距离 × 节点间距"算。
LIST_TRAVEL_FALLBACK = 0.2        # 量不到节点间距时的单档行程(probe 实测间距 ≈0.2)
LIST_TRAVEL_MIN = 0.12            # 最小行程: 至少挪动一个节点
LIST_TRAVEL_MAX = 0.5             # 单次行程上限: 拖过半个屏幕容易甩过头
LIST_SWIPE_MS_MAX = 1600          # 长行程配更长时间, 免得被当成甩动
LIST_ROW_Y_FALLBACK = 0.59        # 量不到节点行 y 时的兜底(probe: 关卡节点 y≈0.59)
LIST_DRAG_MARGIN = 0.06           # 拖动起点离屏幕边缘的最小距离
LIST_LEFT = "left"                # 目标在左: 内容右移(起点在节点簇左侧, 往右拖)
LIST_RIGHT = "right"              # 目标在右: 内容左移(起点在节点簇右侧, 往左拖)
# 扫荡流程按钮文本(与 Raid.py 的资源关一致)
SWEEP_ENTRY = "连续扫荡"
START_SWEEP = "开始扫荡"
DONE = "完成"
CANCEL = "取消"
# 章节卡片上的进度文本: 「章节标题 + 同一行的 x/y」(地图卡片与二级界面右卡同款)
PROGRESS_TEXT_RE = r"^\d+/\d+$"
# 章节标题: N4 / 13 / OCR 只认出 "N" 的情况(注意不能匹配空文本)
CHAPTER_TITLE_RE = r"^(N\d*|\d+)$"
# 顶部资源条(586/2400、4/4)与左下角「任务进度 x/y」的位置范围 —— 这两处形状和
# 章节卡片上的进度文本一模一样, 但点下去弹的是商店/任务面板(真机 probe 实测)
SCREEN_TOP_RATIO = 0.2
SCREEN_BOTTOM_RATIO = 0.85
# 次数设置(弹窗「米诺斯管理系统-体力消耗」, 坐标来自探测, 与资源关同一套 UI)
# 滑条范围 1..5, 两端为 -/+ 按钮; 次数显示在「选择次数」右侧(OCR 常合并成 选择次数3)
SWEEP_PLUS = (0.7164, 0.6458)
SWEEP_MINUS = (0.2875, 0.6458)
SWEEP_COUNT_ROI = [0.25, 0.565, 0.15, 0.07]
# 弹窗滑条右端值受当前体力限制(探测时为 5), 不是游戏硬上限:
# 因此界面允许填 1..20, 实际能加到哪里由弹窗决定, 加不动就按当前次数继续。
SWEEP_MAX = 20
# 迪斯城地图上才会出现的文本(用于确认真的进了地图)
MAP_MARKERS = ("历史模式", "特别行动", "内海", "锈河", "全天开放")
# 会盖住主界面的面板/页面文本(命中就先退掉)
OVERLAY_MARKERS = ("局长信息", "生涯", "称号", "头像框")  # 注意: 禁闭者/管理局 是主界面按钮, 不能放进来
# 主线导航常量是否可用(探测已完成)
NAV_READY = True


@TASKER_MANAGER.add_action(name)
class FarmMaterial(MyCustomAction):

    def run(self, context: Context, argv: MyCustomAction.RunArg) -> bool:
        self.param = self._load_param(argv.custom_action_param)
        if not self.param["materials"]:
            logger.debug("材料刷取: 未选择材料,跳过")
            return True
        logger.info(f"材料刷取 开始")
        clicker = Click(context)
        data = load_material_data()
        progress = self._resolve_progress(clicker)
        # 记录本次主线位置: _goto_chapter 靠它推断旋盘该往哪个方向拖
        self._progress = progress
        key = progress_key(progress)

        remaining = list(self.param["materials"])
        if not remaining:
            logger.debug("材料刷取: 无待刷材料,跳过")
            return True
        if not NAV_READY:
            logger.error("材料刷取: 主线导航坐标尚未探测(见 docs/nav_probe/coords.md), 本次跳过")
            return True

        plans = plan(data, remaining, key)
        try:
            for index, mat in enumerate(remaining):
                entry = plans.get(mat) or {"stage": None, "fallbacks": [], "rejected": []}
                if entry["stage"] is None:
                    logger.warning(f"材料刷取: {mat} 无可用关卡(进度不足),跳过")
                    continue
                chain = ([entry["stage"]] + entry["fallbacks"])[:MAX_CANDIDATES]
                logger.debug("材料刷取: " + mat + " 候选 " + " -> ".join(s["code"] for s in chain))
                result = "unavailable"
                for stage in chain:
                    stamina = f"体力{stage['stamina']}" if stage.get("stamina") else "体力未知"
                    logger.info(f"材料刷取: {mat} -> {stage['code']} {stage['name']}({stamina})")
                    result = self._farm_one(clicker, stage)
                    if result != "unavailable":
                        break
                    logger.warning(f"材料刷取: {stage['code']} 不可用, 回退下一个候选")
                if result == "ok":
                    continue
                if result == "no_stamina":
                    # 体力不足: 本次到此为止; 剩下的材料本次不再尝试(spec §7: 不续刷)
                    skipped = remaining[index + 1:]
                    if skipped:
                        logger.warning("材料刷取: 体力不足, 本次跳过: " + ", ".join(skipped))
                    break
                logger.warning(f"材料刷取: {mat} 本次未刷到, 跳过")
        except StopException:
            # 不续刷: 未完成的材料只体现在日志里, 不写盘(spec §7)
            logger.warning("材料刷取: 手动停止, 未完成的材料不再记录")
            raise
        logger.info("材料刷取: 完成")
        return True

    # ------------------------------------------------------------ 参数
    @staticmethod
    def _to_dict(raw) -> dict:
        """框架传入的是 JSON 字符串(可能被再编码一层), 也可能已是 dict
        与 Raid._to_dict 同款: maa 的 RunArg.custom_action_param 声明为 str。
        """
        value = raw
        for _ in range(3):
            if isinstance(value, dict):
                return value
            if not isinstance(value, str) or not value:
                break
            try:
                value = json.loads(value)
            except ValueError:
                break
        if raw not in (None, ""):
            logger.warning(f"材料刷取: 参数无法解析: {raw!r}")
        return {}

    def _load_param(self, raw) -> dict:
        """键形如 <材料名>checkBox / SweepCountCombo / ProgressModeCombo / ProgressCombo"""
        param = self._to_dict(raw)
        materials = [
            key[: -len("checkBox")]
            for key, value in param.items()
            if key.endswith("checkBox") and value
        ]
        try:
            count = int(param.get("SweepCountCombo", "3"))
        except (TypeError, ValueError):
            count = 3
        return {
            "materials": materials,
            "sweep_count": max(1, min(count, 20)),
            "progress_mode": param.get("ProgressModeCombo", "自动"),
            "progress_manual": param.get("ProgressCombo", "13"),
        }

    # ------------------------------------------------------------ 进度
    def _resolve_progress(self, clicker) -> str:
        """spec 5.1: 手动 > 本次探测 > 缓存 > 默认 13"""
        if self.param["progress_mode"] == "手动":
            return self.param["progress_manual"] or "13"
        detected = self._detect_progress(clicker)
        if detected:
            cfg.main_progress = detected
            save_confg()
            logger.debug(f"材料刷取: 探测到主线进度 {detected}")
            return detected
        if cfg.main_progress:
            logger.debug(f"材料刷取: 探测失败, 使用缓存进度 {cfg.main_progress}")
            return cfg.main_progress
        logger.warning("材料刷取: 探测失败且无缓存, 按默认第13章处理")
        return "13"

    def _detect_progress(self, clicker) -> str:
        """探测最新主线进度       
        向上拖到底是最新区域
        旁边的「x/y」进度文本就是进度; 当前横向位置看不到时再把地图横向拖到最右。
        """
        if not NAV_READY:
            return ""
        if not self._open_map(clicker):
            return ""
        self._drag_dial_to_end(clicker, direction="up")
        for _ in range(3):
            pair = self._find_progress_pair(clicker)
            if pair:
                logger.debug(f"材料刷取: 地图进度 {pair}")
                return pair
            self._drag_map_to_side(clicker, MAP_LEFT, max_steps=MAP_DETECT_STEPS)
        logger.warning("材料刷取: 拖到底仍未找到主线进度文本")
        return ""

    def _drag_dial_to_end(self, clicker, direction="up", max_steps=8) -> None:
        """朝一个方向反复拖旋盘, 直到界面不再变化(到底)"""
        last = None
        for _ in range(max_steps):
            snapshot = tuple(sorted(self._screen_texts(clicker)))
            if snapshot == last:
                break
            last = snapshot
            self._dial_once(clicker, direction)

    def _drag_map_to_side(self, clicker, direction=MAP_LEFT, max_steps=MAP_SCAN_STEPS) -> None:
        """把地图横向滑到某一端: 以当前可见章节节点的 y 为高度, 每次滑一屏, 画面不再变化即到底"""
        anchor = None
        for text, _score, box in self._screen_items(clicker):
            if re.match(STAGE_CODE_RE, text.replace(" ", "")) or re.match(
                r"^[A-Za-z]{0,4}N?\d+$", text.replace(" ", "")
            ):
                anchor = box
                break
        y = (anchor[1] + anchor[3] / 2) / cfg.height if anchor else MAP_ROW_Y_FALLBACK
        if direction == MAP_LEFT:
            begin, end = MAP_DRAG_BEGIN, MAP_DRAG_END
        else:
            begin, end = MAP_DRAG_END, MAP_DRAG_BEGIN
        last = None
        for _ in range(max_steps):
            snapshot = tuple(sorted(self._screen_texts(clicker)))
            if snapshot == last:
                return
            last = snapshot
            clicker.swape([begin, y, 8, 8], [end, y + MAP_DRAG_DRIFT, 8, 8], SWIPE_MS)
            stop_sleep(1.5)

    def _map_find_chapter(self, clicker, chapter) -> bool:
        """在当前区域的地图里横向找目标章节: 先滑到一端找, 找不到再滑到另一端找

        章节是横向一排且可能超过一屏, 滑到两端即可覆盖(区域不超过两屏, 真机实测),
        所以这里不做方向/行程推算 —— 这正是"不在屏幕里就找不到"的修法。
        """
        for direction in (MAP_LEFT, MAP_RIGHT):
            self._drag_map_to_side(clicker, direction)
            if self._click_text(clicker, chapter):
                return True
        return False

    def _find_progress_pair(self, clicker) -> str:
        """在地图区域(y>0.2)里找「章节文本 + x/y 进度」这一对, 返回如 N7-1/6"""
        items = self._screen_items(clicker)
        fractions = [
            (text.replace(" ", ""), box)
            for text, _score, box in items
            if re.match(r"^\d+/\d+$", text.replace(" ", ""))
            and (box[1] + box[3] / 2) / cfg.height > 0.2      # 排除右上角资源计数
        ]
        for frac_text, frac_box in fractions:
            best, best_x = None, -1
            for text, _score, box in items:
                token = text.replace(" ", "")
                if (
                    re.match(r"^N?\d+$", token)
                    and box[0] < frac_box[0]
                    and abs(box[1] - frac_box[1]) < 40
                    and box[0] > best_x
                ):
                    best, best_x = token, box[0]
            if best:
                return f"{best}-{frac_text}"
        return ""

    # ------------------------------------------------------------ 导航
    def _screen_items(self, clicker, sleep_time=0.4) -> list:
        """当前屏幕 OCR 结果 [(text, score, box)]"""
        return clicker.ocr_roi([0, 0, 1, 1], sleep_time=sleep_time) or []

    def _screen_texts(self, clicker, sleep_time=0.4) -> list:
        return [t.replace(" ", "") for t, _s, _b in self._screen_items(clicker, sleep_time)]

    def _click_text(self, clicker, text) -> bool:
        """点击屏幕上与 text 完全相同的文本块; 找不到返回 False

        注意 clicker.ocr_click 是子串匹配(MaaFramework 的 expected): 点 "13" 会命中
        "10:30:00" 这类文本; 所以这里先全屏 OCR 做精确匹配, 再点该文本框中心。
        """
        target = str(text).replace(" ", "")
        for screen_text, _score, box in self._screen_items(clicker):
            if screen_text.replace(" ", "") == target:
                x = (box[0] + box[2] / 2) / cfg.width
                y = (box[1] + box[3] / 2) / cfg.height
                logger.debug(f"材料刷取: 点击 {target} @ ({x:.3f},{y:.3f})")
                clicker.click_rate(x, y)
                return True
        return False

    def _open_map(self, clicker) -> bool:
        """回到副本界面; 返回是否确认在副本界面上
        每轮: 已在副本界面 -> 返回; 有遮挡面板 -> 退掉;
        否则按 OCR 定位: 点「危机管理」标签确保停在卡片视图, 再点那张主线进度卡
        (卡上是"主线位置 + 关卡编号", 用编号正则/地区名定位)。
        """
        clicker.check_return_home()
        for _ in range(4):
            texts = self._screen_texts(clicker)
            if any(marker in texts for marker in MAP_MARKERS):
                if self._click_text(clicker, DIST_CITY):   # 确保在主线(狄斯城)标签
                    stop_sleep(1.0)
                return True
            if any(marker in texts for marker in OVERLAY_MARKERS):
                logger.debug("材料刷取: 关闭遮挡面板")
                clicker.back()
                stop_sleep(1.2)
                continue
            # 1) 确保停在危机管理卡片视图
            self._click_text(clicker, CRISIS_MANAGE_TEXT)
            stop_sleep(1.5)
            # 2) 点进度卡: 优先用卡上的关卡编号(如 ReN7-2), 退而用地区名
            if not self._click_regex(clicker, STAGE_CODE_RE, times=1):
                self._click_text(clicker, CARD_FALLBACK_TEXT)
            stop_sleep(2.5)
        logger.warning(
            "材料刷取: 未能进入副本界面; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _dial_once(self, clicker, direction="down") -> None:
        """按住左侧主线位置标签拖动一档
        关键(真机验证): 必须从"主线位置标签"上按住拖, 且带一点 x 漂移,
        纯竖直滑动游戏不认; duration 用毫秒。
        """
        best = None
        for text, _score, box in self._screen_items(clicker):
            if text.replace(" ", "") in REGION_LABELS:
                cx = (box[0] + box[2] / 2) / cfg.width
                cy = (box[1] + box[3] / 2) / cfg.height
                if best is None or abs(cy - 0.5) < abs(best[2] - 0.5):
                    best = (text, cx, cy)
        if best is None:
            _text, x, y = "兜底位置", *DIAL_FALLBACK
        else:
            _text, x, y = best
        travel = self._dial_travel(clicker)
        drift = DIAL_DRIFT_DOWN if direction == "down" else DIAL_DRIFT_UP
        end_y = y + travel if direction == "down" else y - travel
        clicker.swape([x, y, 8, 8], [x + drift, end_y, 8, 8], DIAL_MS)
        stop_sleep(DIAL_SETTLE)

    def _dial_travel(self, clicker) -> float:
        """拖动行程: 由 OCR 量出的「主线位置标签行距」推算

        实测行程 >=0.16 会被游戏忽略(拉过头), 因此取行距的 0.8 倍并限制在 0.06~0.12。
        """
        ys = sorted(
            (box[1] + box[3] / 2) / cfg.height
            for text, _s, box in self._screen_items(clicker)
            if text.replace(" ", "") in REGION_LABELS
        )
        gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
        if not gaps:
            return DIAL_TRAVEL_FALLBACK
        gap = sorted(gaps)[len(gaps) // 2]
        return max(DIAL_TRAVEL_MIN, min(gap * DIAL_TRAVEL_RATIO, DIAL_TRAVEL_MAX))

    def _chapter_key(self, text) -> tuple:
        """章节文本 -> (系列, 章号); N 系列比数字章节新(与选关规则同一套排序)"""
        return progress_key(str(text))[:2]

    def _visible_chapters(self, clicker) -> list:
        """地图上当前可见的章节号(如 12 / N7), 归一化为 (系列, 章号) 后排序去重
        只取地图区域(y 中心 > 0.2)里的"纯章节号"文本, 排开顶部资源计数以及
        「x/y」进度、「N7-1」关卡编号这类带符号的文本。
        """
        keys = set()
        for text, _score, box in self._screen_items(clicker):
            token = text.replace(" ", "")
            if not re.match(r"^N?\d+$", token):
                continue
            if (box[1] + box[3] / 2) / cfg.height <= 0.2:
                continue
            keys.add(self._chapter_key(token))
        return sorted(keys)

    @staticmethod
    def _region_index(chapter_key) -> int:
        """章节键 -> 主线位置(区域)在 MAP_REGIONS 里的序号; 不在表里返回 -1"""
        if not chapter_key:
            return -1
        for index, (_name, low, high) in enumerate(MAP_REGIONS):
            if low <= tuple(chapter_key) <= high:
                return index
        return -1

    def _current_region(self, clicker) -> int:
        """当前所处的主线位置(区域序号): 先看地图上可见的章节, 读不到再用本次探测的进度"""
        visible = self._visible_chapters(clicker)
        if visible:
            return self._region_index(visible[0])
        return self._region_index(
            self._chapter_key(getattr(self, "_progress", "") or cfg.main_progress)
        )

    def _dial_direction(self, clicker, target, default=DIAL_UP) -> str:
        """推断旋盘该向上还是向下拖; **目标已经在当前区域时返回 ""(不要拖旋盘)**

        区域表(MAP_REGIONS)把章节号换算成主线位置:
          - 目标与当前区域相同 -> "" —— 地图上横向滑就能找到, 拖旋盘反而会跑出这个区域
            (真机踩过: 目标是 N8、屏幕上只有 N5 时, 旧逻辑会往上拖, 其实该把地图往右滑)
          - 区域不同 -> 区域序号大的方向(向上 = 更新的章节, 向下 = 更旧的)
        区域信息拿不到时(章节不在表里、屏幕上一个章节号也没有)退回可见章节区间比较。
        """
        target_region = self._region_index(target)
        current_region = self._current_region(clicker)
        if target_region >= 0 and current_region >= 0:
            if target_region == current_region:
                return ""
            return DIAL_UP if target_region > current_region else DIAL_DOWN
        visible = self._visible_chapters(clicker)
        if visible:
            if target > visible[-1]:
                return DIAL_UP
            if target < visible[0]:
                return DIAL_DOWN
            return default
        current = self._chapter_key(getattr(self, "_progress", "") or cfg.main_progress)
        return DIAL_UP if target > current else DIAL_DOWN

    def _goto_chapter(self, clicker, chapter) -> bool:
        """在地图上把目标章节滚到可见并点开(闭环: 每次拖动后重新观察)

        一个区域的章节在地图上是横向一排且可能超过一屏, 所以顺序是:
          1. 目标已经在当前区域 -> 只在地图里横向找(滑到两端), 找不到就判失败, 不再瞎拖旋盘
          2. 目标在别的区域 -> 按区域表拖旋盘换区域, 换完回到第 1 步
        某一侧旋盘拖不动(画面不再变化)时换另一侧兜一次; 两个方向各有预算, 保证收敛退出。
        """
        if self._click_text(clicker, chapter):
            return True
        target = self._chapter_key(chapter)
        position = getattr(self, "_progress", "") or cfg.main_progress or "未知"
        budgets = {DIAL_UP: MAX_DIAL_DRAGS, DIAL_DOWN: MAX_DIAL_DRAGS}
        direction = self._dial_direction(clicker, target)
        visible = self._visible_chapters(clicker)
        scanned = False
        while True:
            if not direction:                     # 已在目标区域: 只横向找
                if self._map_find_chapter(clicker, chapter):
                    return True
                scanned = True
                break
            if budgets[direction] <= 0:
                break
            logger.debug(
                f"材料刷取: 未见章节 {chapter}(主线位置 {position}, 可见 {visible}), "
                f"拖旋盘向{'上' if direction == DIAL_UP else '下'}"
            )
            self._dial_once(clicker, direction)
            budgets[direction] -= 1
            if self._click_text(clicker, chapter):
                return True
            new_visible = self._visible_chapters(clicker)
            opposite = DIAL_DOWN if direction == DIAL_UP else DIAL_UP
            if new_visible == visible and budgets[opposite] == MAX_DIAL_DRAGS:
                direction = opposite              # 这一侧拖不动了, 换另一侧兜一次
            else:
                direction = self._dial_direction(clicker, target, default=direction)
            visible = new_visible
        if not scanned and self._map_find_chapter(clicker, chapter):   # 换完区域再横向找一遍
            return True
        logger.warning(
            f"材料刷取: 地图上未能找到章节 {chapter}(主线位置 {position}); 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _click_regex(self, clicker, pattern, times=2) -> bool:
        """点击屏幕上匹配正则的第一个文本块(用于"结构稳定但内容变化"的文本)"""
        for _ in range(times):
            for text, _score, box in self._screen_items(clicker):
                cleaned = text.replace(" ", "")
                if re.match(pattern, cleaned):
                    x = (box[0] + box[2] / 2) / cfg.width
                    y = (box[1] + box[3] / 2) / cfg.height
                    logger.debug(f"材料刷取: 点击 {cleaned} @ ({x:.3f},{y:.3f})")
                    clicker.click_rate(x, y)
                    return True
            stop_sleep(0.6)
        # logger.warning(f"材料刷取: 屏幕上没有匹配 {pattern} 的文本")
        return False

    def _stage_code_visible(self, clicker) -> bool:
        """屏幕上是否已经出现关卡编号(说明真的进到关卡列表了)"""
        return any(
            self._is_stage_code(text.replace(" ", ""))
            for text, _score, _box in self._screen_items(clicker)
        )

    @staticmethod
    def _is_stage_code(text) -> bool:
        """屏幕文本是不是关卡节点编号(两套编号样式都认: N7-1 / N3-A1 / Mz-N701)"""
        token = str(text).replace(" ", "")
        return bool(re.match(STAGE_CODE_RE, token) or re.match(STAGE_CODE_EXTRA_RE, token))

    def _chapter_progress_spots(self, clicker) -> list:
        """章节卡片上的「x/y」进度文本位置, 返回比例坐标列表(可能不止一个)

        只认"同一行左侧有章节标题"的进度文本: 地图上的章节卡片、二级界面右侧的
        章节卡片都长这样(N7 + 1/6、N4 + 8/8)。

        关卡列表左下角的「任务进度 6/6」和右上角资源条(586/2400、4/4)形状完全一样,
        但左边没有章节标题 —— 点它们会弹任务面板/商店, 正是这一条把它们挡掉;
        落在页面最下面那一条的(可能是排在下方的章节卡片)排到最后再试, 不直接丢弃。
        """
        items = self._screen_items(clicker)
        spots = []
        for text, _score, box in items:
            if not re.match(PROGRESS_TEXT_RE, text.replace(" ", "")):
                continue
            cy = (box[1] + box[3] / 2) / cfg.height
            if cy <= SCREEN_TOP_RATIO:                  # 顶部资源条
                continue
            has_title = any(
                re.match(CHAPTER_TITLE_RE, t.replace(" ", ""))
                and b[0] < box[0]                       # 标题在进度文本左侧
                and abs(b[1] - box[1]) < 40             # 同一行
                for t, _s, b in items
            )
            if has_title:
                priority = 1 if cy >= SCREEN_BOTTOM_RATIO else 0
                spots.append((priority, (box[0] + box[2] / 2) / cfg.width, cy))
        spots.sort(key=lambda spot: spot[0])
        return [(x, y) for _priority, x, y in spots[:3]]

    def _enter_chapter(self, clicker, chapter) -> bool:
        """点章节节点 -> 进入该章节的关卡列表

        真机: 地图上点章节卡片有时直接进关卡列表, 有时先落在二级界面; 二级界面里
        章节标题常被 OCR 读成 N/1/6(章号丢失), 但标题旁边的「x/y」稳定可读, 点它
        等价于"再点一次章节名"。

        每一步都确认真的进了列表(屏幕上能读到关卡编号), 点错了就试下一个候选;
        始终进不去就返回 False, 让调用方回退到下一个候选关卡, 而不是对着错误的
        界面继续硬点。
        """
        if self._stage_code_visible(clicker):      # 上一步点卡片已经进了列表
            return True
        if not self._click_text(clicker, chapter):
            return False
        stop_sleep(1.5)
        if self._stage_code_visible(clicker):
            return True
        for x, y in self._chapter_progress_spots(clicker):
            logger.debug(f"材料刷取: 点章节卡片的进度文本 @ ({x:.3f},{y:.3f})")
            clicker.click_rate(x, y)
            stop_sleep(1.5)
            if self._stage_code_visible(clicker):
                return True
        logger.warning(
            f"材料刷取: 点章节 {chapter} 后没进关卡列表; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _select_stage(self, clicker, stage) -> bool:
        """在章节关卡列表里选中目标关卡(游戏内编号与 wiki 一致, 如 N7-1 / N3-A1)

        关卡列表是**一整行节点**、按真机顺序从左到右排布(关号小的在左, 同号 A 组在 B 组前),
        整行可能超过一屏, 所以不能只朝一个方向滑:

          1. 用"章内位置"比较目标与屏幕上的节点, 决定往哪边滑(目标在左 -> 内容右移)
          2. 行程 = "目标与最近节点的位置距离 × 实测节点间距", 限制在一个节点到半屏之间
             (近的目标用小行程, 免得一下子滑过头)
          3. 每次滑完重新观察: 目标出现就点; 某一侧画面不再变化(到底)时换另一侧兜一次

        章内位置来自数据里按真机顺序排好的表(`chapter_order`); 该章不在表里时退回关号近似。
        两个方向各有 MAX_LIST_SWIPES 的预算, 保证收敛退出。
        """
        code = stage["code"]
        if self._click_text(clicker, code):
            return True
        chapter = stage.get("chapter") or ""
        positions = self._chapter_positions(chapter)
        target = self._list_pos(code, positions)
        nodes = self._visible_stages(clicker)
        budgets = {LIST_LEFT: MAX_LIST_SWIPES, LIST_RIGHT: MAX_LIST_SWIPES}
        direction = self._list_direction(
            self._node_positions(nodes, chapter, positions), target, default=LIST_RIGHT
        )
        while budgets[direction] > 0:
            same = self._chapter_nodes(nodes, chapter)
            travel = self._list_travel(
                [self._list_pos(node, positions) for node, _x, _y in same],
                target,
                self._list_gap(same),
            )
            logger.debug(
                f"材料刷取: 未见关卡 {code}(屏幕上的节点 "
                f"{[node for node, _x, _y in nodes]}), 向"
                f"{'左' if direction == LIST_LEFT else '右'}滑 {travel:.2f}"
            )
            self._swipe_list(clicker, nodes, direction, travel)
            budgets[direction] -= 1
            if self._click_text(clicker, code):
                return True
            new_nodes = self._visible_stages(clicker)
            opposite = LIST_RIGHT if direction == LIST_LEFT else LIST_LEFT
            if (
                [node for node, _x, _y in new_nodes] == [node for node, _x, _y in nodes]
                and budgets[opposite] == MAX_LIST_SWIPES
            ):
                direction = opposite          # 这一侧滑不动了, 换另一侧兜一次
            else:
                direction = self._list_direction(
                    self._node_positions(new_nodes, chapter, positions), target, default=direction
                )
            nodes = new_nodes
        logger.warning(
            f"材料刷取: 关卡列表里未找到 {code}; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _visible_stages(self, clicker) -> list:
        """关卡列表上当前可见的节点 [(编号, x, y)], 按横坐标排序(左 -> 右)"""
        nodes = []
        for text, _score, box in self._screen_items(clicker):
            code = text.replace(" ", "")
            if not self._is_stage_code(code):
                continue
            nodes.append(
                (code, (box[0] + box[2] / 2) / cfg.width, (box[1] + box[3] / 2) / cfg.height)
            )
        return sorted(nodes, key=lambda node: node[1])

    @staticmethod
    def _chapter_positions(chapter) -> dict:
        """该章 {关卡编号: 章内位置(0 起)} —— 来自数据里按真机顺序排好的表"""
        return position_table(chapter or "")

    @staticmethod
    def _list_pos(code, positions) -> int:
        """节点在章内的位置; 表里没有这个编号时退回关号(仅兜底, 仍与位置同向)"""
        if code in positions:
            return positions[code]
        return FarmMaterial._stage_num(code) or 0

    def _node_positions(self, nodes, chapter, positions) -> list:
        """屏幕上同一章节点的位置列表(排开别套编号的节点)"""
        return [
            self._list_pos(code, positions)
            for code, _x, _y in self._chapter_nodes(nodes, chapter)
        ]

    @staticmethod
    def _chapter_nodes(nodes, chapter) -> list:
        """只留与目标同章的节点

        同一行里会混进别套编号的节点(如 N7 行里的 Mz-N701 / ReN7-2), 它们的序号
        体系不同, 参与"目标在左还是在右"的比较会得出错误方向。
        过滤后一个都不剩时退回全部节点(宁可方向靠猜, 也不要没得比)。
        """
        same = [node for node in nodes if str(node[0]).rsplit("-", 1)[0] == str(chapter)]
        return same or list(nodes)

    @staticmethod
    def _stage_num(code):
        """关卡编号 -> 关号(N3-6 -> 6, N3-A1 -> 1); 解析不出返回 None

        只在拿不到真机顺序表时用作位置的近似(关号小的在左)。
        """
        m = re.search(r"-([A-Za-z]{0,2})(\d+)$", str(code))
        return int(m.group(2)) if m else None

    def _list_gap(self, nodes) -> float:
        """相邻节点的横向间距: 由 OCR 量出的横坐标差取中位数(probe 实测 ≈0.2)"""
        xs = sorted(node[1] for node in nodes)
        gaps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        if not gaps:
            return LIST_TRAVEL_FALLBACK
        return sorted(gaps)[len(gaps) // 2]

    @staticmethod
    def _list_travel(positions, target, gap) -> float:
        """滑动行程: 目标与最近可见节点的位置距离 × 节点间距(一个节点 ~ 半屏之间)"""
        if target is None or not positions:
            return LIST_TRAVEL_FALLBACK
        distance = max(1, min(abs(target - pos) for pos in positions))
        return max(LIST_TRAVEL_MIN, min(distance * gap, LIST_TRAVEL_MAX))

    @staticmethod
    def _list_direction(positions, target, default=LIST_RIGHT) -> str:
        """按"屏幕上的节点位置 vs 目标位置"推断往哪边滑

        位置比屏幕上的都小 -> 目标在左边(内容要右移); 都大 -> 在右边;
        落在可见区间内(本该已经看见) -> 保持当前方向, 免得来回抖。
        """
        if target is None or not positions:
            return default
        if target < min(positions):
            return LIST_LEFT
        if target > max(positions):
            return LIST_RIGHT
        return default

    def _swipe_list(self, clicker, nodes, direction, travel) -> None:
        """横向滑动关卡列表: 从节点簇外侧的空白处按下, 拖 travel 的行程(带 y 偏移)"""
        gap = self._list_gap(nodes)
        xs = [x for _code, x, _y in nodes]
        ys = [y for _code, _x, y in nodes]
        y = sorted(ys)[len(ys) // 2] if ys else LIST_ROW_Y_FALLBACK
        if direction == LIST_LEFT:            # 目标在左: 起点在节点簇左侧, 往右拖
            begin = max(LIST_DRAG_MARGIN, min(xs) - gap / 2) if xs else LIST_DRAG_MARGIN
            end = min(1 - LIST_DRAG_MARGIN, begin + travel)
        else:                                 # 目标在右: 起点在节点簇右侧, 往左拖
            begin = min(1 - LIST_DRAG_MARGIN, max(xs) + gap / 2) if xs else 1 - LIST_DRAG_MARGIN
            end = max(LIST_DRAG_MARGIN, begin - travel)
        # 长行程配更长时间: 手指走得慢一点, 免得游戏按甩动处理而滑过头
        duration = min(LIST_SWIPE_MS_MAX, int(SWIPE_MS * (1 + abs(end - begin))))
        clicker.swape([begin, y, 8, 8], [end, y + LIST_DRAG_DRIFT, 8, 8], duration)
        stop_sleep(1.2)

    def _farm_one(self, clicker, stage) -> str:
        """扫荡单个关卡; 返回 "ok" / "no_stamina" / "unavailable" """
        if not self._open_map(clicker):
            return "unavailable"
        if not self._goto_chapter(clicker, stage["chapter"]):
            clicker.return_home()
            return "unavailable"
        if not self._enter_chapter(clicker, stage["chapter"]):
            clicker.return_home()
            return "unavailable"
        if not self._select_stage(clicker, stage):
            clicker.return_home()
            return "unavailable"
        if not self._click_text(clicker, SWEEP_ENTRY):
            clicker.return_home()
            return "unavailable"
        detail = clicker.ocr_click(CANCEL)          # 体力不足会弹取消
        if detail and detail.success:
            clicker.click_blink()
            clicker.return_home()
            return "no_stamina"
        if not self._set_sweep_count(clicker, self.param["sweep_count"]):
            clicker.back()
            clicker.return_home()
            return "no_stamina"
        if not self._click_text(clicker, START_SWEEP):
            clicker.back()
            clicker.return_home()
            return "unavailable"
        stop_sleep(12)
        clicker.click_rate(0.5, 0.1)                # 升级弹窗(点空白关闭)
        self._click_text(clicker, DONE)
        clicker.return_home()
        return "ok"

    def _set_sweep_count(self, clicker, target: int) -> bool:
        """把滑条次数调到目标值(滑条右端受体力限制, 加不动就按当前次数继续)

        读不到次数(界面差异)或怎么点都不动时不当作体力不足, 告警后按当前次数继续 ——
        体力不足由弹窗自身与「开始扫荡」失败暴露, 避免坐标误差导致提前停机。
        """
        target = max(1, min(int(target), SWEEP_MAX))
        current = self._read_sweep_count(clicker)
        if current is None:
            logger.warning("材料刷取: 未读到扫荡次数, 按界面当前次数继续")
            return True
        stall = 0
        while current < target:
            clicker.click_rate(*SWEEP_PLUS)
            stop_sleep(0.5)
            new = self._read_sweep_count(clicker)
            if new is None or new <= current:
                stall += 1
                if stall >= 3:
                    logger.warning(
                        f"材料刷取: 次数未能从 {current} 加到 {target}, 按当前次数继续"
                    )
                    return True
            else:
                stall = 0
                current = new
        return True

    def _read_sweep_count(self, clicker):
        """读弹窗里的次数; OCR 常把标签与数值合并成「选择次数3」"""
        items = clicker.ocr_roi(SWEEP_COUNT_ROI, sleep_time=0.3) or []
        for text, _score, _box in items:
            if "选择次数" in text.replace(" ", ""):
                digits = re.findall(r"\d+", text)
                if digits:
                    return int(digits[-1])
        for text, _score, _box in items:
            digits = re.findall(r"\d+", text)
            if digits:
                return int(digits[-1])
        return None

    def stop(self) -> None:
        pass
