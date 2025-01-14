
"""经过测试 cv2.VideoCapture 的 read 函数并不能获取实时流的最新帧
而是按照内部缓冲区中顺序逐帧的读取，opencv会每过一段时间清空一次缓冲区
但是清空的时机并不是我们能够控制的，因此如果对视频帧的处理速度如果跟不上接受速度
那么每过一段时间，在播放时(imshow)时会看到画面突然花屏，甚至程序直接崩溃
在网上查了很多资料，处理方式基本是一个思想
使用一个临时缓存，可以是一个变量保存最新一帧，也可以是一个队列保存一些帧
然后开启一个线程读取最新帧保存到缓存里，用户读取的时候只返回最新的一帧
这里我是使用了一个变量保存最新帧
注意：这个处理方式只是防止处理（解码、计算或播放）速度跟不上输入速度
而导致程序崩溃或者后续视频画面花屏，在读取时还是丢弃一些视频帧
"""

import threading

import cv2
import ObjectDetectionModule as odm
import SerialModule as sm
import numpy as np
import base64
import time, sys, os
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')

imgstring = 0
frameWidth = 640
frameHeight = 480        # 像素640*480
filp = 2
rePose = 1              # 手柄是否参与 1：未参与
global conter           # 未监测到目标倒计时
conter=100              # 倒计时100
perrorLR, perrorUD = 0, 0  # 初始误差
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")  # 人脸检测
serr = sm.initConnection('192.168.1.69', 7018)  # 本机设备    网址加端口号（485控制器的） 转台


class RTSCapture(cv2.VideoCapture):
    """Real Time Streaming Capture.
    这个类必须使用 RTSCapture.create 方法创建，请不要直接实例化
    """

    _cur_frame = None
    _reading = False
    schemes = ["rtsp://", "rtmp://"]  # 用于识别实时流


    @staticmethod
    def create(url, *schemes):
        """实例化&初始化
        rtscap = RTSCapture.create("rtsp://example.com/live/1")
        or
        rtscap = RTSCapture.create("http://example.com/live/1.m3u8", "http://")
        """
        rtscap = RTSCapture(url)
        rtscap.frame_receiver = threading.Thread(target=rtscap.recv_frame, daemon=True)
        rtscap.schemes.extend(schemes)
        if isinstance(url, str) and url.startswith(tuple(rtscap.schemes)):
            rtscap._reading = True
        elif isinstance(url, int):
            # 这里可能是本机设备
            pass

        return rtscap

    def isStarted(self):
        """替代 VideoCapture.isOpened() """
        ok = self.isOpened()
        if ok and self._reading:
            ok = self.frame_receiver.is_alive()
        return ok

    def recv_frame(self):
        """子线程读取最新视频帧方法"""
        while self._reading and self.isOpened():
            ok, frame = self.read()
            if not ok: break
            self._cur_frame = frame
        self._reading = False

    def read2(self):
        """读取最新视频帧
        返回结果格式与 VideoCapture.read() 一样
        """
        frame = self._cur_frame
        self._cur_frame = None
        return frame is not None, frame

    def start_read(self):
        """启动子线程读取视频帧"""
        self.frame_receiver.start()
        self.read_latest_frame = self.read2 if self._reading else self.read

    def stop_read(self):
        """退出子线程方法"""
        self._reading = False
        if self.frame_receiver.is_alive(): self.frame_receiver.join()

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
    kLR = [0.4, 0.4, 0.5]
    kUD = [0.3, 0.1, 0.3]
    if cx!=-1:  # 死循环
        # PID控制
        errorLR = w // 2 - cx  # 识别框中心与图框中心在x轴上的距离
        errorUD = h // 2 - cy  # 识别框中心与图框中心在x轴上的距离
        posX1 = kLR[0] * errorLR + kLR[1] * (errorLR - perrorLR)  # 比例和积分分量
        posY1 = kUD[0] * errorUD + kUD[1] * (errorUD - perrorUD)  # 比例和积分分量

        # 使用微分项
        derrorLR = errorLR - perrorLR
        derrorUD = errorUD - perrorUD
        posX1 += kLR[2] * derrorLR  # 添加微分分量
        posY1 += kUD[2] * derrorUD  # 添加微分分量

        # 更新误差积分
        perrorLR = errorLR
        perrorUD = errorUD

        # 将误差映射到输出值
        posX = np.interp(posX1, [-w // 2, w // 2], [20, 160])
        posY = np.interp(posY1, [-w // 2, w // 2], [20, 160])

        data = [posX, posY]
        sm.sendData(serr, data)
if __name__ == '__main__':
    rtscap = RTSCapture.create('rtsp://admin:123456@192.168.1.102:554/h264/ch1/sub/av_stream')     # sys.argv[1]
    rtscap.start_read()  # 启动子线程并改变 read_latest_frame 的指向
    fps = 0.0
    while rtscap.isStarted():
        ok, frame = rtscap.read_latest_frame()  # read_latest_frame() 替代 read()
        if not ok:
            if cv2.waitKey(100) & 0xFF == ord('q'): break
            continue



        # 调整图像大小，先缩小，提高检测速度，之后在进行放大
        frame = cv2.resize(frame, (0, 0), None, 0.5, 0.5)  # 以0，0为中心宽和高都缩小0.5倍  输入图像 FF 01 00 07 00 63 6B
        imgObjects, objects = odm.findObjects(frame, faceCascade, 1.08, 10)  # 使用识别函数文件检测到图像 imgObjects图框/objects识别款
        if len(objects) != 1:  # 没有监测到目标 PELCO-D
            if 100 >= conter > 80:
                conter = conter - 1
            elif 80 >= conter > 0:
                conter = conter - 1
                d = bytes.fromhex('FF 01 00 00 00 00 01')  # 停止命令
                serr.send(d)
            elif conter == 0:
                conter = 0
                if rePose != 0:  # 手柄未参与操作  rePose=1
                    d = bytes.fromhex('FF 01 00 00 00 00 01')  # 巡航
                    serr.send(d)
                else:  # 手柄参与操作
                    pass
            else:
                pass
            print(conter)
        else:  # 检测到目标
            conter = 100
            pass

        cx, cy, imgObjects = findCenter(imgObjects, objects)
        h, w, c = imgObjects.shape
        # print(h,w,c)# 图像的高240、宽320,c=3 线粗
        cv2.line(imgObjects, (w // 2, 0), (w // 2, h), (255, 0, 255), 1)  # 画出图框中心点十字交叉线
        cv2.line(imgObjects, (0, h // 2), (w, h // 2), (255, 0, 255), 1)
        trackObject(cx, cy, w, h)  # 转动转台
        img = cv2.resize(imgObjects, (0, 0), None, 3, 3)
        imgstring = base64.b64encode(img)
        print(type(imgstring))

        #帧处理代码写这里

        cv2.imshow("cam", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    rtscap.stop_read()
    rtscap.release()
    cv2.destroyAllWindows()

