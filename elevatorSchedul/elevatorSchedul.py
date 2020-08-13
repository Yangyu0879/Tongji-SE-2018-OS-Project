import threading
from functools import partial
import time
from PyQt5 import QtCore, QtGui
import sys


class PCB():
    def __init__(self,PID):
        self.PID=PID
        self.state=0 #当前状态，上行，静止或下行
        self.last_state=0#前一刻状态，上行，静止或下行
        self.location=1#当前电梯所在的位置
        self.downfloor=[0]*42#记录下还没有来得及处理的下行请求
        self.upfloor=[0]*42#记录下还没有来得及处理的上行请求
        self.upSequence=[]#上行请求的序列
        self.downSequence=[]#下行请求的序列
        self.isPause=0#判断开关门按钮是否被按下
        self.alert=0#判断警报


class elevator_schedul():
    def __init__(self, ui):
        self.ui=ui
        self.elevator_PCB=[]
        for i in range(1, 6):#产生5部电梯
            self.elevator_PCB.append(PCB(i))
        for i in range(1, 20):  # 上行按钮与监听函数绑定
            self.ui.up_btn[i].clicked.connect(partial(self.upbutton_listen, i))
        for i in range(2, 21):  # 下行按钮与监听函数绑定
            self.ui.down_btn[i].clicked.connect(partial(self.downbutton_listen, i))
        for i in range(1, 6):
            for j in range(1, 21):  # 数字按钮与监听函数绑定
                self.ui.number_btn[i][j].clicked.connect(partial(self.numberbtn_listen, i, j))
        for i in range(1, 6):# 打开按钮与监听函数绑定
            self.ui.open_btn[i].clicked.connect(partial(self.openbtn_listen, i))
        for i in range(1, 6):# 关闭按钮与监听函数绑定
            self.ui.close_btn[i].clicked.connect(partial(self.closebtn_listen, i))
        for i in range(1, 6):# 警报按钮与监听函数绑定
            self.ui.alert_btn[i].clicked.connect(partial(self.alertbtn_listen, i))
        for i in range(1, 6):  # 加载线程
            self.thread(i)


    # 将请求加入电梯elevator_number的下行序列
    def append_downSequence(self,elevator_number,btn_number):
        self.elevator_PCB[elevator_number-1].downSequence.append(btn_number)
        self.elevator_PCB[elevator_number-1].downSequence = list(set(self.elevator_PCB[elevator_number-1].downSequence))#去除重复元素
        self.elevator_PCB[elevator_number-1].downSequence.sort()#排序
        self.elevator_PCB[elevator_number-1].downSequence.reverse()#倒置

    # 将请求加入电梯elevator_number的上行序列
    def append_upSequence(self,elevator_number,btn_number):               
        self.elevator_PCB[elevator_number-1].upSequence.append(btn_number)  
        self.elevator_PCB[elevator_number-1].upSequence = list(set(self.elevator_PCB[elevator_number-1].upSequence))#去除重复元素
        self.elevator_PCB[elevator_number-1].upSequence.sort()#排序

    # 监听上行按钮
    def upbutton_listen(self, btn_number):
        self.ui.up_btn[btn_number].setStyleSheet("QPushButton{border-image: url(icon/up_pressed.png)}")#设置图标
        upbtn_distance = [100, 100, 100, 100, 100, 100]  # 该列表用于记录某楼层发出上行请求时,五部电梯到达楼层所要走的距离，初始化为一个足够大的数
        requestIsUp = {}  # 记录上行请求是否在电梯上方或本层
        for i in range(1, 6):
            if (btn_number - self.elevator_PCB[i-1].location) >= 0:
                requestIsUp[i] = True
            else:
                requestIsUp[i] = False
        for i in range(1, 6):
            if self.elevator_PCB[i-1].state == 1:  # 上行状态
                if requestIsUp[i]:  # 请求在上方或本层
                    upbtn_distance[i] = abs(btn_number - self.elevator_PCB[i-1].location)  # 当前位置距请求位置距离
                else:  # 请求在下方
                    upbtn_distance[i] = abs(self.elevator_PCB[i-1].location - self.elevator_PCB[i-1].upSequence[len(self.elevator_PCB[i-1].upSequence) - 1]) \
                                        + abs(btn_number - self.elevator_PCB[i-1].upSequence[len(self.elevator_PCB[i-1].upSequence) - 1])  # 当前位置距终点距离 + 终点距请求位置距离
            elif self.elevator_PCB[i-1].state == 0:  # 静止状态
                upbtn_distance[i] = abs(btn_number - self.elevator_PCB[i-1].location)  # 当前位置距请求位置距离
            elif self.elevator_PCB[i-1].state == -1:  # 下行状态
                upbtn_distance[i] = abs(self.elevator_PCB[i-1].location - self.elevator_PCB[i-1].downSequence[len(self.elevator_PCB[i-1].downSequence) - 1]) \
                                    + abs(btn_number - self.elevator_PCB[i-1].downSequence[len(self.elevator_PCB[i-1].downSequence) - 1])  # 当前位置距终点距离 + 终点距请求位置距离
        elevator_number = upbtn_distance.index(min(upbtn_distance))  # 记录距离最短的电梯
        if self.elevator_PCB[elevator_number-1].state == 1:  # 上行状态
            if requestIsUp[elevator_number]:  # 请求在上方或本层
                self.append_upSequence(elevator_number,btn_number)
            else:  # 请求在下方
                self.elevator_PCB[elevator_number-1].upfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层上行请求
        elif self.elevator_PCB[elevator_number-1].state == 0:  # 静止状态
            if requestIsUp[elevator_number]:  # 请求在上方或本层
                self.append_upSequence(elevator_number,btn_number)
            else:  # 请求在下方
                self.elevator_PCB[elevator_number-1].upfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层上行请求
        elif self.elevator_PCB[elevator_number-1].state == -1:  # 下行状态
            self.elevator_PCB[elevator_number-1].upfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层上行请求

    # 监听下行按钮
    def downbutton_listen(self, btn_number):
        self.ui.down_btn[btn_number].setStyleSheet("QPushButton{border-image: url(icon/down_pressed.png)}")
        downbtn_distance = [100, 100, 100, 100, 100, 100]  # 该列表用于记录某楼层发出下行请求时,五部电梯到达楼层所要走的距离，初始化为一个足够大的数
        requestIsDown = {}  # 请求是否在电梯下方或包括本层
        for i in range(1, 6):
            if (btn_number - self.elevator_PCB[i-1].location) <= 0:
                requestIsDown[i] = True
            else:
                requestIsDown[i] = False
        for i in range(1, 6):
            if self.elevator_PCB[i-1].state == -1:  # 下行状态
                if requestIsDown[i]:  # 请求在下方或本层
                    downbtn_distance[i] = abs(self.elevator_PCB[i-1].location - btn_number)  # 当前位置距请求位置距离
                else:  # 请求在下方
                    downbtn_distance[i] = abs(self.elevator_PCB[i-1].location - self.elevator_PCB[i-1].downSequence[len(self.elevator_PCB[i-1].downSequence) - 1]) \
                                          + abs(btn_number - self.elevator_PCB[i-1].downSequence[len(self.elevator_PCB[i-1].downSequence) - 1])  # 当前位置距终点距离 + 终点距请求位置距离
            elif self.elevator_PCB[i-1].state == 0:  # 静止状态
                downbtn_distance[i] = abs(self.elevator_PCB[i-1].location - btn_number)  # 当前位置距请求位置距离
            elif self.elevator_PCB[i-1].state == 1:  # 上行状态
                downbtn_distance[i] = abs(self.elevator_PCB[i-1].location - self.elevator_PCB[i-1].upSequence[len(self.elevator_PCB[i-1].upSequence) - 1]) \
                                      + abs(btn_number - self.elevator_PCB[i-1].upSequence[len(self.elevator_PCB[i-1].upSequence) - 1])  # 当前位置距终点距离 + 终点距请求位置距离
        elevator_number = downbtn_distance.index(min(downbtn_distance))  # 记录距离最短的电梯
        if self.elevator_PCB[elevator_number-1].state == -1:  # 下行状态
            if requestIsDown[elevator_number]:  # 请求在下方或本层
                self.append_downSequence(elevator_number,btn_number)
            else:  # 请求在上方
                self.elevator_PCB[elevator_number-1].downfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层下行请求
        elif self.elevator_PCB[elevator_number-1].state == 0:  # 静止状态
            if requestIsDown[elevator_number]:  # 请求在下方或本层
                self.append_downSequence(elevator_number,btn_number)
            else:  # 请求在上方
                self.elevator_PCB[elevator_number-1].downfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层下行请求
        elif self.elevator_PCB[elevator_number-1].state == 1:  # 上行状态
            self.elevator_PCB[elevator_number-1].downfloor[btn_number] = 1  # 记录电梯将处理但未处理的楼层下行请求

    # 监听电梯楼层数字按钮
    def numberbtn_listen(self, elevator_number, btn_number):
        if self.elevator_PCB[elevator_number-1].state == 0:  # 电梯处于静止状态
            if self.elevator_PCB[elevator_number-1].location > btn_number:  # 电梯当前位置在请求楼层之上
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.append_downSequence(elevator_number,btn_number)
            if self.elevator_PCB[elevator_number-1].location < btn_number:  # 电梯当前位置在请求楼层之下
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.append_upSequence(elevator_number,btn_number)
        elif self.elevator_PCB[elevator_number-1].state == 1:  # 电梯处于上行状态
            if self.elevator_PCB[elevator_number-1].location < btn_number:  # 电梯当前位置在请求楼层之下
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.append_upSequence(elevator_number,btn_number)
            else:
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.elevator_PCB[elevator_number-1].downfloor[btn_number] = 1 #记录电梯将处理但未处理的楼层下行请求
        elif self.elevator_PCB[elevator_number-1].state == -1:  # 电梯处于下行状态
            if self.elevator_PCB[elevator_number-1].location > btn_number:  # 电梯当前位置在请求楼层之上
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.append_downSequence(elevator_number,btn_number)
            else:
                self.ui.number_btn[elevator_number][btn_number].setStyleSheet("QPushButton{border-image: url(icon/" + str(btn_number) + "_pressed.png)}")
                self.elevator_PCB[elevator_number-1].upfloor[btn_number] = 1 #记录电梯将处理但未处理的楼层上行请求

    #监听打开按钮
    def openbtn_listen(self,elevator_number):
        self.ui.open_btn[elevator_number].setStyleSheet("QPushButton{border-image: url(icon/open_pressed.png)}")
        self.elevator_PCB[elevator_number-1].isPause=1#设置门被打开

    #监听关闭按钮
    def closebtn_listen(self,elevator_number):
        self.ui.close_btn[elevator_number].setStyleSheet("QPushButton{border-image: url(icon/close_pressed.png)}")
        self.elevator_PCB[elevator_number-1].isPause=0#设置门被关闭
        self.ui.open_btn[elevator_number].setStyleSheet(self.ui.openbtn_style)
        self.ui.close_btn[elevator_number].setStyleSheet(self.ui.closebtn_style)

    #监听警报按钮
    def alertbtn_listen(self,elevator_number):
        if self.elevator_PCB[elevator_number-1].alert==0:
            self.ui.alert_btn[elevator_number].setStyleSheet("QPushButton{border-image: url(icon/alert_pressed.png)}")
            self.elevator_PCB[elevator_number-1].alert=1
        else:
            self.ui.alert_btn[elevator_number].setStyleSheet(self.ui.alertbtn_style)

    # 执行完上行动作恢复静止后，处理执行动作时产生的但未处理的请求
    def elevator_finish_up(self, elevator_number):
        i = 20
        while i >= 1:  # 倒序处理执行动作时产生的但未处理的下行请求
            if self.elevator_PCB[elevator_number-1].downfloor[i] == 1:
                if i > self.elevator_PCB[elevator_number-1].location:  # 上方存在执行动作时产生的但未处理的下行请求
                    self.elevator_PCB[elevator_number-1].upSequence.append(i)  # 将最高楼层的下行请求加入上行序列,继续上行
                    self.elevator_PCB[elevator_number-1].upSequence = list(set(self.elevator_PCB[elevator_number-1].upSequence))
                    self.elevator_PCB[elevator_number-1].state = 1
                    break
                # 上方不存在执行动作时产生的但未处理的下行请求
                self.elevator_PCB[elevator_number-1].downfloor[i] = 0
                self.append_downSequence(elevator_number,i)
                self.elevator_PCB[elevator_number-1].state = -1
            i = i - 1
        # 不存在下行请求，处理执行动作时产生的但未处理的上行请求（该请求只可能在下方）
        if self.elevator_PCB[elevator_number-1].state == 0:
            for i in range(1, 21):  # 正序处理
                if self.elevator_PCB[elevator_number-1].upfloor[i] == 1:
                    self.elevator_PCB[elevator_number-1].downSequence.append(i)  # 将最底楼层的下行请求加入下行序列,开始下行
                    self.elevator_PCB[elevator_number-1].downSequence = list(set(self.elevator_PCB[elevator_number-1].downSequence))
                    self.elevator_PCB[elevator_number-1].state = -1
                    break

    # 执行完下行动作恢复静止后，处理执行动作时产生的但未处理的请求
    def elevator_finish_down(self, elevator_number):
        for i in range(1,21):  # 正序处理执行动作时产生的但未处理的上行请求
            if self.elevator_PCB[elevator_number-1].upfloor[i] == 1:
                if i < self.elevator_PCB[elevator_number-1].location:  # 下方存在执行动作时产生的但未处理的上行请求
                    self.elevator_PCB[elevator_number-1].downSequence.append(i)  # 将最低楼层的上行请求加入下行序列,继续下行
                    self.elevator_PCB[elevator_number-1].downSequence = list(set(self.elevator_PCB[elevator_number-1].downSequence))
                    self.elevator_PCB[elevator_number-1].state = -1
                    break
                # 下方不存在执行动作时产生的但未处理的上行请求
                self.elevator_PCB[elevator_number-1].upfloor[i] = 0
                self.append_upSequence(elevator_number,i)
                self.elevator_PCB[elevator_number-1].state = 1
        # 不存在上行请求，处理执行动作时产生的但未处理的下行请求（该请求只可能在上方）
        if self.elevator_PCB[elevator_number-1].state == 0:
            i = 20  # 倒序处理
            while i >= 1:
                if self.elevator_PCB[elevator_number-1].downfloor[i] == 1:
                    self.elevator_PCB[elevator_number-1].upSequence.append(i)  # 将最高楼层的下行请求加入上行序列,开始上行
                    self.elevator_PCB[elevator_number-1].upSequence = list(set(self.elevator_PCB[elevator_number-1].upSequence))
                    self.elevator_PCB[elevator_number-1].state = 1
                    break
                i = i - 1

    # 每趟动画执行完后，对该趟动画执行时产生的未能执行的数据进行处理
    def finish_anim(self, elevator_number):
        if self.elevator_PCB[elevator_number-1].last_state == 0:  # 电梯初始状态
            self.elevator_finish_down(elevator_number)  # 执行完下行动作恢复静止后，处理执行动作时产生的但未处理的请求
        elif self.elevator_PCB[elevator_number-1].last_state == 1:  # 执行完上行动作后
            self.elevator_finish_up(elevator_number)  # 执行完上行动作恢复静止后，处理执行动作时产生的但未处理的请求
        elif self.elevator_PCB[elevator_number-1].last_state == -1:  # 执行完下行动作后
            self.elevator_finish_down(elevator_number)  # 执行完下行动作恢复静止后，处理执行动作时产生的但未处理的请求

    # 创建线程
    def thread(self, elevator_number):
        t = threading.Thread(target=partial(self.elevator_anim, elevator_number))
        t.setDaemon(True)
        t.start()

    # 加载上行序列动画
    def elevator_up_anim(self, elevator_number):
        while len(self.elevator_PCB[elevator_number-1].upSequence):  # 如果上行序列非空
            self.elevator_PCB[elevator_number-1].state = 1  # 置电梯状态为上行状态
            upSequence_0 = self.elevator_PCB[elevator_number-1].upSequence[0]  # 记录当前上行序列的第一个任务
            j = abs(self.elevator_PCB[elevator_number-1].upSequence[0] - self.elevator_PCB[elevator_number-1].location)  # 当前位置与上行序列的第一个任务相差的层数
            i = 1
            while i <= j:
                if upSequence_0 == self.elevator_PCB[elevator_number-1].upSequence[0]:  # 上行序列第一个任务未更新
                    time.sleep(0.8)
                    self.elevator_PCB[elevator_number-1].location+=1  # 更新location[elevator_number]
                    self.ui.elevator_picture[elevator_number].setGeometry(QtCore.QRect((20+60*(elevator_number-1))*1.5,(565-27* (self.elevator_PCB[elevator_number-1].location-1))*1.5, 30*1.5, 30*1.5))
                    self.ui.location_label[elevator_number].setText(str(self.elevator_PCB[elevator_number-1].location))  # 更新楼层显示
                else:  # 上行序列第一个任务更新
                    j = abs(self.elevator_PCB[elevator_number-1].upSequence[0] - self.elevator_PCB[elevator_number-1].location)  # 更新当前位置与上行序列的第一个任务相差的层数
                    upSequence_0 = self.elevator_PCB[elevator_number-1].upSequence[0]  # 更新当前上行序列的第一个任务的记录
                    i = 0  # 重置i，考虑到后面存在+1，将i置为0
                i = i + 1
            time.sleep(0.8)  # 电梯到达目的楼层，停顿
            if self.elevator_PCB[elevator_number-1].upSequence[0] < 20:  # 还原按钮样式
                self.ui.up_btn[self.elevator_PCB[elevator_number-1].upSequence[0]].setStyleSheet(self.ui.upbtn_style)
            self.ui.number_btn[elevator_number][self.elevator_PCB[elevator_number-1].upSequence[0]].setStyleSheet(
                "QPushButton{border-image: url(icon/" + str(self.elevator_PCB[elevator_number-1].upSequence[0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(icon/" + str(self.elevator_PCB[elevator_number-1].upSequence[0]) + ".png)}"
                "QPushButton:pressed{border-image: url(icon/" + str(self.elevator_PCB[elevator_number-1].upSequence[0]) +
                "_pressed.png)}")
            if self.elevator_PCB[elevator_number-1].isPause==1:#判断是否有open按钮被按下
                time.sleep(2)
                self.ui.open_btn[elevator_number].setStyleSheet(self.ui.openbtn_style)
                self.elevator_PCB[elevator_number-1].isPause=0;
            del self.elevator_PCB[elevator_number-1].upSequence[0]  # 删除序列中已处理完的楼层
        self.elevator_PCB[elevator_number-1].last_state = self.elevator_PCB[elevator_number-1].state  # 上行序列处理完毕，记录本次状态
        self.elevator_PCB[elevator_number-1].state = 0  # 上行序列处理完毕，取消电梯上行状态

    # 加载下行序列动画
    def elevator_down_anim(self, elevator_number):
        while len(self.elevator_PCB[elevator_number-1].downSequence):  # 如果下行序列非空
            self.elevator_PCB[elevator_number-1].state = -1  # 置电梯状态为下行状态
            downSequence_0 = self.elevator_PCB[elevator_number-1].downSequence[0]  # 记录当前下行序列的第一个任务
            j = abs(self.elevator_PCB[elevator_number-1].downSequence[0] - self.elevator_PCB[elevator_number-1].location)  # 当前位置与下行序列的第一个任务相差的层数
            i = 1
            while i <= j:
                if downSequence_0 == self.elevator_PCB[elevator_number-1].downSequence[0]:  # 下行序列第一个任务未更新
                    time.sleep(0.8)
                    self.elevator_PCB[elevator_number-1].location-=1
                    self.ui.elevator_picture[elevator_number].setGeometry(QtCore.QRect((20+60*(elevator_number-1))*1.5,(565-27* (self.elevator_PCB[elevator_number-1].location-1))*1.5, 30*1.5,30*1.5))
                    self.ui.location_label[elevator_number].setText(str(self.elevator_PCB[elevator_number-1].location))
                else:  # 下行序列第一个任务更新
                    j = abs(self.elevator_PCB[elevator_number-1].downSequence[0] - self.elevator_PCB[elevator_number-1].location)  # 更新当前位置与下行序列的第一个任务相差的层数
                    downSequence_0 = self.elevator_PCB[elevator_number-1].downSequence[0]  # 更新当前下行序列的第一个任务的记录
                    i = 0  # 重置i，考虑到后面存在+1，将i置为0
                i = i + 1
            time.sleep(0.8)  # 电梯到达目的楼层，停顿
            if self.elevator_PCB[elevator_number-1].downSequence[0] > 1:  # 还原按钮样式
                self.ui.down_btn[self.elevator_PCB[elevator_number-1].downSequence[0]].setStyleSheet(self.ui.downbtn_style)
            self.ui.number_btn[elevator_number][self.elevator_PCB[elevator_number-1].downSequence[0]].setStyleSheet(
                "QPushButton{border-image: url(icon/" + str(self.elevator_PCB[elevator_number-1].downSequence[0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(icon/" +
                str(self.elevator_PCB[elevator_number-1].downSequence[0]) + ".png)}"
                "QPushButton:pressed{border-image: url(icon/" +
                str(self.elevator_PCB[elevator_number-1].downSequence[0]) + "_pressed.png)}")
            if self.elevator_PCB[elevator_number-1].isPause==1:#判断是否有open按钮被按下
                time.sleep(2)
                self.ui.open_btn[elevator_number].setStyleSheet(self.ui.openbtn_style)
                self.elevator_PCB[elevator_number-1].isPause=0;
            del self.elevator_PCB[elevator_number-1].downSequence[0]  # 删除序列中已处理完的楼层
        self.elevator_PCB[elevator_number-1].last_state = self.elevator_PCB[elevator_number-1].state  # 下行序列处理完毕，记录本次状态
        self.elevator_PCB[elevator_number-1].state = 0  # 下行序列处理完毕，取消电梯下行状态



    # 加载电梯动画
    def elevator_anim(self, elevator_number):
        while True:
            if self.elevator_PCB[elevator_number-1].state == 0:  # 电梯处于静止状态
                self.elevator_up_anim(elevator_number)  # 加载上行序列动画
                self.finish_anim(elevator_number)
                self.elevator_down_anim(elevator_number) # 加载下行序列动画
                self.finish_anim(elevator_number)
            elif self.elevator_PCB[elevator_number-1].state == 1:  # 电梯处于上行状态
                self.elevator_up_anim(elevator_number)  # 加载上行序列动画
                self.elevator_finish_up(elevator_number)
            elif self.elevator_PCB[elevator_number-1].state == -1:  # 电梯处于下行状态
                self.elevator_down_anim(elevator_number)  # 加载下行序列动画
                self.elevator_finish_down(elevator_number)
