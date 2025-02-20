import curses#cueses 非windows,需额外转化
import SerialModule as sm
import time
serr = sm.initConnection('192.168.1.69', 7018)
# 定义示例函数
def up():
    d = bytes.fromhex('FF 01 00 20 00 00 21')  # 放大
    serr.send(d)
    print("Up key was pressed")


def down():
    d = bytes.fromhex('FF 01 00 40 00 00 41')  # 缩小
    serr.send(d)
    print("Down key was pressed")


def left():
    d = bytes.fromhex("FF 01 00 04 FF 00 04")# 左
    serr.send(d)
    print("Left key was pressed")


def right():
    d = bytes.fromhex('FF 01 00 02 05 00 08')  # 向右
    serr.send(d)
    print("Right key was pressed")


def space():
    d = bytes.fromhex('FF 01 00 00 00 00 01')  # 停止
    serr.send(d)
    print("Space key was pressed")


# 初始化屏幕
def init_screen(stdscr):
    # 关闭键盘回显
    curses.noecho()
    # 将输入模式设置为非阻塞
    curses.cbreak()
    # 将键盘输入设置为原始模式
    curses.curs_set(0)
    # 获取键盘输入
    stdscr.keypad(True)


# 主函数
def main(stdscr):
    init_screen(stdscr)

    while True:
        # 获取键盘输入
        key = stdscr.getch()

        # 根据按键执行相应函数
        if key == curses.KEY_UP:
            up()
        elif key == curses.KEY_DOWN:
            down()
        elif key == curses.KEY_LEFT:
            left()
        elif key == curses.KEY_RIGHT:
            right()
        elif key == ord(' '):  # 空格键的ASCII码是32
            space()
        elif key == ord('q'):  # 如果按下'q'，退出程序
            break


# 初始化curses并运行主函数
curses.wrapper(main)
