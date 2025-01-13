import cv2
import ObjectDetectionModule as odm
import SerialModule as sm
import numpy as np

import base64
import time, sys, os
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')
from HPSocket import TcpPush
imgstring = 0
frameWidth = 640
frameHeight = 480        # 像素640*480
filp = 2
rePose = 1              # 手柄是否参与 1：未参与
global conter           # 未监测到目标倒计时
conter=100              # 倒计时100

cap = cv2.VideoCapture('rtsp://admin:123456@192.168.1.108:554/h264/ch1/sub/av_stream')
serr = sm.initConnection('192.168.1.69', 7018)     # 本机设备    网址加端口号（485控制器的） 转台
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")  # 人脸检测

perrorLR, perrorUD = 0, 0  # 初始误差
# 查找人脸，并绘制方块及中心点，及x y线
def findCenter(imgObjects, objects):
    cx, cy = -1, -1
    if len(objects) != 0:
        x, y, w, h = objects[0]    # x，y为识别框左上角的坐标值，w,h为识别框的宽和高////objects以元组的形式将参数存储
        cx = x + w//2              # cx识别框中心 的x坐标
        cy = y + h//2              # cy识别框中心 的y坐标q
        cv2.circle(imgObjects, (cx, cy), 1, (0, 255, 0), cv2.FILLED)    # 画圆，（cx,cy）为圆心坐标，2为半径
        ih, iw, ic = imgObjects.shape
        # print(ih,iw,ic)          # 图像的高ih为240，图像的宽iw为320
        cv2.line(imgObjects, (iw//2, cy), (cx, cy), (0, 255, 0), 1)
        cv2.line(imgObjects, (cx, ih//2), (cx, cy), (0, 255, 0), 1)     # 画出识别框中心与图框中心的x,y垂直距离直线
    return cx, cy, imgObjects


# 返回人脸中心点到，图像中间的距离

datas = [0, 1]
datae = [0]
def trackObject(cx, cy, w, h):  # cx,cy为识别框中心点坐标，w,h为图像宽和高

    global perrorLR, perrorUD
    kLR = [0.5, 0.5]
    kUD = [0.5, 0.5]
    if cx!=-1:  # 死循环
        # PID控制
        errorLR = w//2 - cx                                      # 识别框中心与图框中心在x轴上的距离，，此处定义为x轴上的偏差
        posX1 = kLR[0] * errorLR + kLR[1] * (errorLR-perrorLR)   # 比例偏差值（不确定）P分量=当前误差*系数+上次的误差增量*系数
        posX = np.interp(posX1, [-w//2, w//2], [20, 160])
        perrorLR = errorLR
        errorUD = h//2 - cy
        posY1 = kUD[0] * errorUD + kUD[1] * (errorUD-perrorUD)
        posY = np.interp(posY1, [-w//2, w//2], [20, 160])
        perrorUD = errorUD
        data = [posX, posY]
        sm.sendData(serr, data)

while True:
    success, img = cap.read()
    print(type(img))
    # 调整图像大小，先缩小，提高检测速度，之后在进行放大
    img = cv2.resize(img, (0, 0), None, 0.5, 0.5)  # 以0，0为中心宽和高都缩小0.5倍  输入图像 FF 01 00 07 00 63 6B
    imgObjects, objects = odm.findObjects(img, faceCascade, 1.08, 10)  # 使用识别函数文件检测到图像 imgObjects图框/objects识别款
    if len(objects) != 1:                                   # 没有监测到目标 PELCO-D
        if 100 >= conter > 80:
            conter = conter - 1
        elif 80 >= conter > 0:
            conter = conter - 1
            d = bytes.fromhex('FF 01 00 00 00 00 01')       # 停止命令
            serr.send(d)
        elif conter == 0:
            conter = 0
            if rePose != 0:                                 # 手柄未参与操作  rePose=1
                d = bytes.fromhex('FF 01 00 00 00 00 01')   # 巡航
                serr.send(d)
            else:                                           # 手柄参与操作
                pass
        else:
            pass
        print(conter)
    else:                                                   # 检测到目标
        conter = 100
        pass

    cx, cy, imgObjects = findCenter(imgObjects, objects)
    h, w, c = imgObjects.shape
    # print(h,w,c)# 图像的高240、宽320,c=3 线粗
    cv2.line(imgObjects, (w//2, 0), (w//2, h), (255, 0, 255), 1)    # 画出图框中心点十字交叉线
    cv2.line(imgObjects, (0, h//2), (w, h//2), (255, 0, 255), 1)
    trackObject(cx, cy, w, h)                                       # 转动转台
    img = cv2.resize(imgObjects, (0, 0), None, 3, 3)
    imgstring = base64.b64encode(img)
    print(type(imgstring))
    cv2.imshow("Image", img)
    # 当按下q键，退出循环，并发送复位给arduinouno
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sm.sendData(serr, [90, 90], 3)
        break