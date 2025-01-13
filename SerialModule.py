import time
import socket


def initConnection(portNo, baudRate):
    try:
        scc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        scc.connect((portNo, baudRate))
        print("Device connected")
        return scc
    except:
        print("Not Connected")


def sendData(sock, data):
    try:
        if data[0] > 95 and data[1] > 92:                       # 目标在左上，向左上移
            if 1 < data[0] - data[1]:
                d = bytes.fromhex('FF 01 00 04 05 00 0A')       # 向左
                sock.send(d)
                print("向左上移:1.向左")
            elif 1 < data[1] - data[0]:
                d = bytes.fromhex('FF 01 00 08 00 05 0E')       # 向上
                sock.send(d)
                print("向左上移:2.向上")
            else:
                d = bytes.fromhex('FF 01 00 0C 05 05 17')       # 向左上移（基本不会执行）
                sock.send(d)
                print("向左上移")
        elif 85 > data[0] and 88 < data[1] < 92:                # 中右
            d = bytes.fromhex('FF 01 00 02 05 00 08')
            print("中右1")
            sock.send(d)
            print("中右2")
        elif data[0] > 95 and data[1] < 92:                     # 目标在左下，向左下移
            if 1 < data[0] -90 - (90 - data[1]):
                d = bytes.fromhex('FF 01 00 04 05 00 0A')       # 向左
                sock.send(d)
                print("向左下:1.向左")
            elif 1 < 90 - data[0] - (data[1] - 90):
                d = bytes.fromhex('FF 01 00 10 00 05 16')       # 向下
                sock.send(d)
                print("向左下:2.向下")
            else:
                d = bytes.fromhex('FF 01 00 14 05 05 1F ')      # 向左下
                sock.send(d)
                print("向左下")
        elif data[0] < 95 and data[1] > 92:                     # 目标在右上，向右上移
            time.sleep(0.1)
            if 1 < data[0] - 90 - (90 - data[1]):
                d = bytes.fromhex('FF 01 00 08 00 05 0E')       # 向上
                sock.send(d)
                print("向右上:1.向上")
            elif 1 < 90 - data[0] - (data[1] - 90):
                d = bytes.fromhex('FF 01 00 02 05 00 08')       # 向右
                sock.send(d)
                print("向右上:2.向左")
            else:
                d = bytes.fromhex('FF 01 00 0A 05 05 15')       # 向右上
                sock.send(d)
                print("向右上")
        elif data[0] < 85 and data[1] < 88:                     # 目标在右下，向右下移
            if 1 < data[0] - data[1]:
                d = bytes.fromhex('FF 01 00 10 00 05 16')       # 向下
                sock.send(d)
                print("向左上移:1.向下")
            elif 1 < data[1] - data[0]:
                d = bytes.fromhex('FF 01 00 02 05 00 08')       # 向右
                sock.send(d)
                print("向右上移:2.向右")
            else:
                d = bytes.fromhex('FF 01 00 12 05 05 1D')       # 向右下
                sock.send(d)
                print("向右下移")
        elif 85 <= data[0] <= 95 and 88 <= data[1] <= 92:       # 停止+射击
            d = bytes.fromhex('FF 01 00 00 00 00 01')
            sock.send(d)
            print("停止")
        elif 85 < data[0] < 95 and 88 > data[1]:                # 中下
            d = bytes.fromhex('FF 01 00 10 00 05 16')
            sock.send(d)
        elif 85 < data[0] < 95 and 92 < data[1]:                # 中上
            d = bytes.fromhex('FF 01 00 08 00 05 0E')
            sock.send(d)
        elif 95 < data[0] and 88 < data[1] < 92:                # 中左
            d = bytes.fromhex('FF 01 00 04 05 00 0A')
            sock.send(d)
            print("中左")
        else:
            pass
    except:
         print("Data Transmission Failed ........")
         d = bytes.fromhex('FF 01 00 00 00 00 01')
         sock.send(d)



# if __name__ == "__main__":
#     sot = initConnection("192.168.1.69", 7018)
#     while True:
#         sendData(sot, [50, 255], 3)
#         time.sleep(0)
#         sendData(sot, [50, 0], 3)
#         time.sleep(0)
