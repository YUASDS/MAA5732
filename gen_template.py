# -*- coding: utf-8 -*-
"""从游戏截图自动裁剪按钮模板 + 输出 ROI 比例坐标
用法:
  python gen_template.py <截图路径> [输出目录]
作用:
  1. 用 det 检测所有文字/按钮框
  2. 每个框(带 padding)裁剪成模板图, 存到输出目录
  3. 打印每个框的 ROI 比例坐标(供 smart_click 的 roi 参数用)
然后人工把模板图重命名成按钮文字名(如 "领取.png"), 即可配合 smart_click 使用。
"""
import sys, os, cv2, numpy as np, onnxruntime as ort

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(BASE, "assets", "resource", "model", "ocr")
OUT_DEFAULT = os.path.join(BASE, "assets", "resource", "image", "templates")
PAD = 4  # 裁剪时外扩像素

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "screen.png")
    out_dir = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT
    os.makedirs(out_dir, exist_ok=True)

    img = cv2.imread(img_path)
    H, W = img.shape[:2]
    det = ort.InferenceSession(MODEL + r"\det.onnx", providers=["CPUExecutionProvider"])

    scale = 960 / H
    nw = int(W * scale) // 32 * 32
    inp = cv2.resize(img, (nw, 960)).astype(np.float32) / 255.0
    prob = det.run(None, {det.get_inputs()[0].name: inp.transpose(2, 0, 1)[None]})[0][0][0]
    mask = (prob > 0.3).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for c in contours:
        if cv2.contourArea(c) < 80:
            continue
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect).astype(np.float32)
        box[:, 0] /= scale
        box[:, 1] /= scale
        xs, ys = box[:, 0], box[:, 1]
        boxes.append([xs.min(), ys.min(), xs.max(), ys.max()])
    boxes = sorted(boxes, key=lambda b: (round(b[1] / 30), b[0]))

    print(f"image={W}x{H}  boxes={len(boxes)}  out={out_dir}\n")
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        cx0, cy0 = max(0, int(x0) - PAD), max(0, int(y0) - PAD)
        cx1, cy1 = min(W, int(x1) + PAD), min(H, int(y1) + PAD)
        crop = img[cy0:cy1, cx0:cx1]
        name = f"tmpl_{i:03d}.png"
        cv2.imwrite(os.path.join(out_dir, name), crop)
        # ROI 比例坐标 [x, y, w, h]
        rx, ry = cx0 / W, cy0 / H
        rw, rh = (cx1 - cx0) / W, (cy1 - cy0) / H
        print(f"{name:16s} roi=[{rx:.3f}, {ry:.3f}, {rw:.3f}, {rh:.3f}]  中心比例=({(cx0+cx1)/2/W:.3f}, {(cy0+cy1)/2/H:.3f})")

if __name__ == "__main__":
    main()
