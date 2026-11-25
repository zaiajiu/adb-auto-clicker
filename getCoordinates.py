from pynput import mouse

print("=============================================")
print("🖱️ 鼠标坐标监听已启动！")
print("👉 请把鼠标移动到模拟器画面里，点击你想记录的位置。")
print("👉 按 Ctrl+C 可以停止脚本。")
print("=============================================")

def on_click(x, y, button, pressed):
    # 只有按下鼠标左键时才触发打印（排除松开鼠标的操作）
    if pressed and button == mouse.Button.left:
        print(f"📍 你点击了坐标: X = {x}, Y = {y}")

# 启动监听
with mouse.Listener(on_click=on_click) as listener:
    listener.join()