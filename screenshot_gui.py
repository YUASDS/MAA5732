# -*- coding: utf-8 -*-
"""截图 + 圈选标注工具：在截图上框选按钮，累积成「按钮→坐标」知识库。
之后 MAA5732 直接查库点坐标，不再 OCR。
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess, os, time, json
import cv2
from PIL import Image, ImageTk

BASE = os.path.dirname(os.path.abspath(__file__))
ADB = os.path.join(BASE, "assets", "adb", "adb.exe")
ADDRESS = "127.0.0.1:16384"
SHOT_DIR = os.path.join(BASE, "screenshots")
BUTTONS_JSON = os.path.join(BASE, "assets", "config", "buttons.json")

CANVAS_W, CANVAS_H = 900, 506   # 16:9

def load_buttons():
    try:
        return json.load(open(BUTTONS_JSON, encoding="utf-8"))
    except Exception:
        return {}

def save_buttons(db):
    json.dump(db, open(BUTTONS_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

class App:
    def __init__(self, root):
        self.root = root
        self.img = None          # 原图 BGR
        self.photo = None        # 显示用
        self.sx = self.sy = 1.0  # 缩放比例
        self.press = None        # 框选起点
        self.rect_id = None
        root.title("截图 + 圈选标注 — 框选按钮，输入名字")
        root.geometry("940x680")

        top = tk.Frame(root); top.pack(pady=6)
        tk.Button(top, text="📷 截图  (F8)", command=self.shot, height=1,
                  font=("", 11)).pack(side="left", padx=6)
        tk.Button(top, text="查看已标注", command=self.show_db).pack(side="left", padx=6)
        self.status = tk.StringVar(value="截图后，用鼠标在画面上框选按钮，再输入名字")
        tk.Label(root, textvariable=self.status, fg="#0a7a2f").pack()

        self.cv = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="#222",
                            cursor="crosshair")
        self.cv.pack(padx=10, pady=4)
        self.cv.bind("<ButtonPress-1>", self.on_press)
        self.cv.bind("<B1-Motion>", self.on_drag)
        self.cv.bind("<ButtonRelease-1>", self.on_release)
        root.bind("<F8>", lambda e: self.shot())

    def shot(self):
        os.makedirs(SHOT_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SHOT_DIR, f"shot_{ts}.png")
        with open(path, "wb") as f:
            subprocess.run([ADB, "-s", ADDRESS, "exec-out", "screencap", "-p"],
                           stdout=f, stderr=subprocess.DEVNULL, check=True, timeout=20)
        self.img = cv2.imread(path)
        self.show_img()
        self.status.set(f"已截图 {os.path.basename(path)} — 框选按钮")

    def show_img(self):
        H, W = self.img.shape[:2]
        self.sx, self.sy = CANVAS_W / W, CANVAS_H / H
        rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb).resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(pil)
        self.cv.delete("all")
        self.cv.create_image(0, 0, anchor="nw", image=self.photo)

    def on_press(self, e):
        self.press = (e.x, e.y)
        self.rect_id = self.cv.create_rectangle(e.x, e.y, e.x, e.y, outline="#00ff00", width=2)

    def on_drag(self, e):
        if self.rect_id:
            x0, y0 = self.press
            self.cv.coords(self.rect_id, x0, y0, e.x, e.y)

    def on_release(self, e):
        if not self.press:
            return
        x0, y0 = self.press
        x1, y1 = e.x, e.y
        if abs(x1 - x0) < 5 or abs(y1 - y0) < 5:
            return
        # 映射回原图比例坐标
        H, W = self.img.shape[:2]
        rx0, ry0 = x0 / self.sx / W, y0 / self.sy / H
        rx1, ry1 = x1 / self.sx / W, y1 / self.sy / H
        name = simpledialog.askstring("按钮名", "这个框是什么按钮？（如：一键领取）")
        if not name:
            return
        name = name.strip()
        db = load_buttons()
        db[name] = {
            "roi": [round(min(rx0, rx1), 3), round(min(ry0, ry1), 3),
                    round(abs(rx1 - rx0), 3), round(abs(ry1 - ry0), 3)],
            "center": [round((rx0 + rx1) / 2, 3), round((ry0 + ry1) / 2, 3)],
        }
        save_buttons(db)
        self.cv.create_rectangle(x0, y0, x1, y1, outline="#00ff00", width=2)
        self.cv.create_text(min(x0, x1), max(y0, y1) + 12, text=name,
                            fill="#00ff00", anchor="nw")
        self.status.set(f"已标注「{name}」 center=({db[name]['center'][0]:.3f},{db[name]['center'][1]:.3f})  共 {len(db)} 个")
        self.press = None

    def show_db(self):
        db = load_buttons()
        if not db:
            messagebox.showinfo("已标注", "还没有标注任何按钮")
            return
        lines = [f"{k}: center={v['center']} roi={v['roi']}" for k, v in db.items()]
        messagebox.showinfo(f"已标注 {len(db)} 个按钮", "\n".join(lines))

root = tk.Tk()
App(root)
root.mainloop()
