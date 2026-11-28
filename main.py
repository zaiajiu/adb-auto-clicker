import os

QUEUE = 3
#升级页面分所有建筑(0)，基础建筑(1)，资源建筑的升级(2),通过修改变量select进行选择，默认所有建筑
select = 0
#研究升级页面分武器研究(0)，基础资源建筑(1)
study_select = 1
#排除顶部的叉号按钮
ROI_AVOID_TOP = (0, 200, 900, 1600)
import cv2
from ppadb.client import Client as AdbClient
import time
import numpy as np
#.\adb.exe devices
import subprocess

# 定义所有关闭按钮模板
CLOSE_TEMPLATES = [
    "./image/closeButtons.png",
    "./image/closeButtons2.png",
    "./image/closeButtons3.png",
    # "./image/closeButtons4.png",
    "./image/confirm.png",
]
FREE_TEMPLATES = [
    "./image/freeButtons.png",
]
CONDITION_NOT_TEMPLATES = [
    "./image/conditionNot.png",
    "./image/conditionNot1.png",
]

#建筑升级
#队列按钮（取消叉号）
QUEUE_TEMPLATES = [
    "./image/queueButtons.png",
]
#点击升级按钮
UPGRADE_TEMPLATES = [
    "./image/upgradeButtons.png",
]
#升级页面按钮
UPGRADES_TEMPLATES = [
    "./image/upgrades.png",
]
#基础建筑升级页面
BASIC_TEMPLATES = [
    "./image/BasicBuilding.png",
]
#资源建筑升级页面
RESOURCE_TEMPLATES = [
    "./image/ResourceBuilding.png",
]
#游戏启动图标
GAME_TEMPLATES = [
    "./image/game.png",
    "./image/game1.png",
]

###研究升级
#研究队列按钮（取消叉号）
STUDY_QUEUE_TEMPLATES = [
    "./image/studyqueueButton.png",
]
#研究升级按钮
STUDY_UPGRADE_TEMPLATES = [
    "./image/studyUpgradeButton.png",
]
#研究页面按钮
STUDY_TEMPLATES = [
    "./image/studyButton.png",
]
#武器升级
WEAPON_TEMPLATES = [
    "./image/studyWeaponButton.png",
]
#基地资源研究
STUDY_RESOURCE_TEMPLATES = [
    "./image/studyResourceButton.png",
]
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout, r.stderr)
    return r.returncode

run([r"D:\Daily\MuMu\MuMuPlayer\nx_main\adb.exe", "connect", "127.0.0.1:5555"])
time.sleep(2)
run([r"D:\Daily\MuMu\MuMuPlayer\nx_main\adb.exe", "devices"])

#截图比对模板，返回所有按钮
def find_all_buttons(device, template_paths, threshold=0.8, roi=None, save_result=False):
    """
        支持同时寻找多张模板图，并支持限定区域。
        template_paths 是一个列表，例如 ["./image/close_1.png", "./image/close_2.png"]
        roi: 可选，格式为 (x1, y1, x2, y2)。如果不传则全屏找。
        save_result: 默认 False，不保存；调用时传 True 才把匹配结果标红保存到 Result 目录。
    """
    all_buttons = []
    matched_rects = []  # 仅在 save_result=True 时使用

    # 先截一次全屏图
    try:
        screen_bytes = device.screencap()
        img_array = np.frombuffer(screen_bytes, np.uint8)
        full_screen_gray = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        if full_screen_gray is None:
            return []
    except Exception:
        return []

    # 如果有传 roi，就进行裁剪
    screen_gray = full_screen_gray
    offset_x, offset_y = 0, 0

    if roi is not None:
        x1, y1, x2, y2 = roi
        h_img, w_img = full_screen_gray.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w_img, x2), min(h_img, y2)

        if x2 > x1 and y2 > y1:
            screen_gray = full_screen_gray[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
        else:
            return []

    for template_path in template_paths:
        template = cv2.imread(template_path, 0)
        if template is None:
            continue

        h, w = template.shape
        if screen_gray.shape[0] < h or screen_gray.shape[1] < w:
            continue

        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            real_x = pt[0] + offset_x
            real_y = pt[1] + offset_y

            is_new = True
            for (bx, by) in all_buttons:
                if abs(real_x + w // 2 - bx) < w * 0.5 and abs(real_y + h // 2 - by) < h * 0.5:
                    is_new = False
                    break
            if is_new:
                all_buttons.append((real_x + w // 2, real_y + h // 2))
                if save_result:
                    matched_rects.append((real_x, real_y, w, h, os.path.basename(template_path)))

    # 仅在需要时标红保存
    if save_result and matched_rects:
        full_screen_color = cv2.cvtColor(full_screen_gray, cv2.COLOR_GRAY2BGR)
        for (x, y, w, h, label) in matched_rects:
            cv2.rectangle(full_screen_color, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(full_screen_color, label, (x, max(y - 5, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        result_dir = "Result"
        os.makedirs(result_dir, exist_ok=True)
        save_path = os.path.join(result_dir, "result.png")
        cv2.imwrite(save_path, full_screen_color)

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
        cccButtons = find_all_buttons(device, ["./image/ccc.png"], roi=ROI_AVOID_TOP, save_result=True)
        if cccButtons:
            print("关闭弹窗")
            cccButtons.sort(key=lambda p: p[1])
            cx, cy = cccButtons[0]
            cx = cx + 80
            device.shell(f"input tap {cx} {cy}")
            time.sleep(1.5)
            continue


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
                print("没有免费按钮或已经全部点击，，，，")

        ##选择页面
        if select ==1:
            basicButtons = find_all_buttons(device, BASIC_TEMPLATES)
            basicCount = len(basicButtons)
            if basicCount:
                print("发现基础页面")
                cx, cy = basicButtons[0]
                basicButtons.sort(key=lambda p: p[1])
                print("切换基础页面，，，")
                device.shell(f"input tap {cx} {cy}")
        if select ==2:
            resourceButtons = find_all_buttons(device, RESOURCE_TEMPLATES)
            resourceCount = len(resourceButtons)
            if resourceCount:
                print("发现资源页面")
                resourceButtons.sort(key=lambda p: p[1])
                cx, cy = resourceButtons[0]
                print("切换资源页面，，，")
                device.shell(f"input tap {cx} {cy}")


        # ================= 2. 处理升级队列 =================
        queueButtons = find_all_buttons(device, QUEUE_TEMPLATES)
        queueCount = len(queueButtons)
        print(f"当前队列：{queueCount}")

        if queueCount<QUEUE:
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
                print("⚠️ 没找到升级按钮，正在关闭弹窗和寻找升级页面...")
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
                    print("没有找到升级页面，尝试启动游戏。。。")
                    gameButton = find_all_buttons(device,GAME_TEMPLATES)
                    if len(gameButton):
                        gameButton.sort(key=lambda p: p[1])
                        cx, cy = (gameButton[0])
                        device.shell(f"input tap {cx} {cy}")
                        print(f"找到游戏并启动：{cx}, {cy}")

        else:
            print(f"✅ 队列已满 ({QUEUE}/{QUEUE})，等待升级完成...")
            print(f"本次运行已经升级：{Count}次")
            time.sleep(3)
            print("队列已满，前往研究升级。。。")
            closeButtons = find_all_buttons(device, CLOSE_TEMPLATES)
            closeButtons.sort(key=lambda p: p[1])
            cx, cy = closeButtons[0]
            device.shell(f"input tap {cx} {cy}")
            studyButtons = find_all_buttons(device, STUDY_TEMPLATES)
            cx, cy = studyButtons[0]
            device.shell(f"input tap {cx} {cy}")
            time.sleep(3)
            if study_select == 0:
                studyWeaponButtons = find_all_buttons(device, WEAPON_TEMPLATES)
                if studyWeaponButtons:
                    cx, cy = studyWeaponButtons[0]
                    device.shell(f"input tap {cx} {cy}")
                else:
                    print("找不到武器科技界面")
            if study_select == 1:
                studyResourceButtons = find_all_buttons(device, STUDY_RESOURCE_TEMPLATES)
                if studyResourceButtons:
                    cx, cy = studyResourceButtons[0]
                    device.shell(f"input tap {cx} {cy}")
                else:
                    print("找不到基地科技界面")

            studyQueueButtons = find_all_buttons(device, STUDY_QUEUE_TEMPLATES)
            studyQueueCount = len(studyQueueButtons)
            if studyQueueCount < QUEUE:
                studyUpgradeButtons = find_all_buttons(device, STUDY_UPGRADE_TEMPLATES)
                conditionNot = find_all_buttons(device, CONDITION_NOT_TEMPLATES)
                conditionNotCount = len(conditionNot)
                studyUpgradeButtons.sort(key=lambda p: p[1])
                cx, cy = studyUpgradeButtons[conditionNotCount]
                device.shell(f"input tap {cx} {cy}")
                print(f"🚀 当前队列 {studyQueueCount}/{QUEUE}")

    except Exception as e:
        print(f"⚠️ 发生错误: {e}")
        time.sleep(2)

