import cv2

def findObjects(img, objectCascade, scaleF = 1.1, minN = 4):

    imgObjects = img.copy()
    imgGray = cv2.cvtColor(imgObjects, cv2.COLOR_BGR2GRAY)
    objects = objectCascade.detectMultiScale(imgGray, scaleF, minN)
    objectsOut = []                                                             # 创建空列表
    for (x, y, w, h) in objects:
        cv2.rectangle(imgObjects, (x, y), (x+w, y+h), (255, 0, 255), 2)         # 在图像上绘制矩形
        objectsOut.append([[x, y, w, h], w*h])                                  # append方法用在列表末尾添加新的对象

    objecctsOut = sorted(objectsOut, key=lambda x: x[1], reverse=True)
    
    return imgObjects, objects

# def main():
#     img = cv2.imread("../Resources/testPh1.jpg")
#     faceCascade = cv2.CascadeClassifier("../Resources/haarcascade_frontalface_default.xml")
#     imgObjects, objects = findObjects(img, faceCascade)
#     cv2.imshow("Output",imgObjects)
#     cv2.waitKey(0)
#
# if __name__ == "__main__":
#     main()
