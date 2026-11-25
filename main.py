QUEUE = 3
#排除顶部的叉号按钮
ROI_AVOID_TOP = (0, 200, 900, 1600)
import cv2
from ppadb.client import Client as AdbClient
import time
import numpy as np
#.\adb.exe devices
import subprocess

# 定义你的所有关闭按钮模板
CLOSE_TEMPLATES = [
    "./image/closeButtons.png",
    "./image/closeButtons2.png",
    "./image/closeButtons3.png",
]
FREE_TEMPLATES = [
    "./image/freeButtons.png",
]
QUEUE_TEMPLATES = [
    "./image/queueButtons.png",
]
UPGRADE_TEMPLATES = [
    "./image/upgradeButtons.png",
]
UPGRADES_TEMPLATES = [
    "./image/upgrades.png",
]
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout, r.stderr)
    return r.returncode

run([r"D:\Daily\MuMu\MuMuPlayer\nx_main\adb.exe", "connect", "127.0.0.1:5555"])
time.sleep(2)
run([r"D:\Daily\MuMu\MuMuPlayer\nx_main\adb.exe", "devices"])

#截图比对模板，返回所有按钮
def find_all_buttons(device, template_paths, threshold=0.8, roi=None):
    """
        支持同时寻找多张模板图，并支持限定区域。
        template_paths 是一个列表，例如 ["./image/close_1.png", "./image/close_2.png"]
        roi: 可选，格式为 (x1, y1, x2, y2)。如果不传则全屏找。
    """
    all_buttons = []

    # 先截一次全屏图
    try:
        screen_bytes = device.screencap()
        img_array = np.frombuffer(screen_bytes, np.uint8)
        full_screen_gray = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        if full_screen_gray is None:
            return []
    except Exception:
        return []

    #如果有传 roi，就进行裁剪
    screen_gray = full_screen_gray
    offset_x, offset_y = 0, 0

    if roi is not None:
        x1, y1, x2, y2 = roi
        h_img, w_img = full_screen_gray.shape
        # 防止越界
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w_img, x2), min(h_img, y2)

        if x2 > x1 and y2 > y1:
            screen_gray = full_screen_gray[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1  # 记录偏移量，计算真实坐标时加回来
        else:
            return []

    # 遍历列表里的每一张图
    for template_path in template_paths:
        template = cv2.imread(template_path, 0)
        if template is None:
            continue

        h, w = template.shape
        # 如果模板比裁剪后的区域还大，直接跳过
        if screen_gray.shape[0] < h or screen_gray.shape[1] < w:
            continue

        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            # 真实的左上角坐标
            real_x = pt[0] + offset_x
            real_y = pt[1] + offset_y

            is_new = True
            for (bx, by) in all_buttons:
                # 去重：距离太近认为是同一个
                if abs(real_x + w // 2 - bx) < w * 0.5 and abs(real_y + h // 2 - by) < h * 0.5:
                    is_new = False
                    break
            if is_new:
                # 存入真实的中心坐标
                all_buttons.append((real_x + w // 2, real_y + h // 2))

    return all_buttons



print("正在寻找设备...")
client = AdbClient(host="127.0.0.1", port=5037)
devices = client.devices()
if not devices:
    print("❌ 没有找到模拟器！")
else:
    for d in devices:
        print(f"✅ 找到设备: {d.serial}")

#拿设备
device = devices[0]
print(f"已连接到设备：{device.serial}")
Count = 0
while True:
    try:
        # ================= 0. 兜底：优先处理弹窗 =================
        closeButtons = find_all_buttons(device, CLOSE_TEMPLATES, threshold=0.8,roi=ROI_AVOID_TOP)
        if closeButtons:
            # 如果屏幕上有弹窗关闭按钮，优先点它
            closeButtons.sort(key=lambda p: p[1])  # 从上到下
            cx, cy = closeButtons[0]  # 只点最上面的一个
            print(f"🛑 发现弹窗，点击关闭: ({cx}, {cy})")
            device.shell(f"input tap {cx} {cy}")
            time.sleep(1.5)  # 等弹窗关闭动画播完
            continue  # ⚠️ 关完弹窗，直接跳过后续逻辑，重新截图

        # ================= 1. 处理免费按钮 =================
        freeButtons = find_all_buttons(device, FREE_TEMPLATES)
        if freeButtons:
            freeButtons.sort(key=lambda p: p[1])
            cx, cy = freeButtons[0]
            print(f"🎁发现免费按钮{len(freeButtons)}个， 点击免费按钮: ({cx}, {cy})")
            device.shell(f"input tap {cx} {cy}")
            time.sleep(3)  # 点完免费，等界面刷新
            print("当前免费按钮已点击，准备开始处理下一个免费按钮或处理队列。。。")
            Count = Count + 1
            continue
        else:
                print("免费按钮已经全部点击，准备开始处理队列，，，，")


        # ================= 2. 处理升级队列 =================
        queueButtons = find_all_buttons(device, QUEUE_TEMPLATES)
        queueCount = len(queueButtons)
        print(f"当前队列：{queueCount}")

        if queueCount < QUEUE:
            upgradeButtons = find_all_buttons(device, UPGRADE_TEMPLATES)
            print(f"当前升级按钮：{len(upgradeButtons)}")
            if upgradeButtons:
                upgradeButtons.sort(key=lambda p: p[1])
                cx, cy = upgradeButtons[0]
                print(f"🚀 当前队列 {queueCount}/{QUEUE}，点击升级按钮: ({cx}, {cy})")
                device.shell(f"input tap {cx} {cy}")
                time.sleep(3)  # 点完升级，等动画反应（可能会弹提示）
                continue

            else:
                print("⚠️ 队列未满，但没找到升级按钮，等待重试...")
                time.sleep(2)
                #可能网络错误弹回主页并出现弹窗，先把弹窗点掉
                closeButtons = find_all_buttons(device, CLOSE_TEMPLATES)
                if len(closeButtons):
                    closeButtons.sort(key=lambda p: p[1])
                    cx, cy = closeButtons[0]
                    device.shell(f"input tap {cx} {cy}")
                    print("关闭了一个弹窗，寻找升级页面....")
                upgradesButtons = find_all_buttons(device, UPGRADES_TEMPLATES)
                if len(upgradesButtons):
                    upgradesButtons.sort(key=lambda p: p[1])
                    cx, cy = (upgradesButtons[0])
                    device.shell(f"input tap {cx} {cy}")
                    print(f"点击坐标{cx}, {cy}")
                    print("进入了升级页面，开始自动升级。。。")
                else:
                    print("没有找到升级页面，可能存在弹窗")


        else:
            print(f"✅ 队列已满 ({QUEUE}/{QUEUE})，等待升级完成...")
            print(f"本次运行已经升级：{Count}次")
            time.sleep(3)

    except Exception as e:
        print(f"⚠️ 发生错误: {e}")
        time.sleep(2)

