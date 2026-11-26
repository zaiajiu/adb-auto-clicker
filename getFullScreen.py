from ppadb.client import Client as AdbClient
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

#####截图全屏
print("正在截屏，请稍等...")
screen_bytes = device.screencap()

with open("fullScreen/fullScreen.png", "wb") as f:
    f.write(screen_bytes)

print("🎉 截屏成功！请去左侧项目栏查看 closeButtons3.png")