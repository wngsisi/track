import SerialModule as sm
import time
#第四位为速度，
serr = sm.initConnection('192.168.1.69', 7018)
d= bytes.fromhex('FF 01 00 40 00 00 41')#缩小
#d= bytes.fromhex('FF 01 00 20 00 00 21')#放大
#d= bytes.fromhex("FF 01 00 04 FF 00 3C") ;serr.send(d);time.sleep(3)#快速左转

#d = bytes.fromhex('FF 01 00 04 05 00 0A')  # 向左
print("发送命令")
serr.send(d)
print("开始执行")
time.sleep(1)
d=bytes.fromhex('FF 01 00 00 00 00 01')#停止
serr.send(d)

print("完成")

