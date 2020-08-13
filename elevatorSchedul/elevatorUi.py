from PyQt5 import QtCore, QtGui, QtWidgets,uic
import sys
from elevatorSchedul import elevator_schedul

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 900)
        MainWindow.setStyleSheet("#MainWindow{border-image:url(icon/background.png)}")
        self.Wwidget = QtWidgets.QWidget(MainWindow)
        self.Wwidget.resize(960, 900)

        self.upbtn_style = "QPushButton{border-image: url(icon/up_hover.png)}"\
            "QPushButton:hover{border-image: url(icon/up.png)}"\
            "QPushButton:pressed{border-image: url(icon/up_pressed.png)}"
        self.downbtn_style = "QPushButton{border-image: url(icon/down_hover.png)}" \
            "QPushButton:hover{border-image: url(icon/down.png)}" \
            "QPushButton:pressed{border-image: url(icon/down_pressed.png)}"
        self.openbtn_style = "QPushButton{border-image: url(icon/open_hover.png)}"\
            "QPushButton:hover{border-image: url(icon/open.png)}"\
            "QPushButton:pressed{border-image: url(icon/open_pressed.png)}"
        self.closebtn_style = "QPushButton{border-image: url(icon/close_hover.png)}" \
            "QPushButton:hover{border-image: url(icon/close.png)}" \
            "QPushButton:pressed{border-image: url(icon/close_presssed.png)}"
        self.alertbtn_style = "QPushButton{border-image: url(icon/alert_hover.png)}" \
            "QPushButton:hover{border-image: url(icon/alert.png)}" \
            "QPushButton:pressed{border-image: url(icon/alert_presssed.png)}"

        #画电梯
        self.elevator_picture = {}
        for i in range(1, 6):
            self.elevator_picture[i] = QtWidgets.QLabel(MainWindow)
            self.elevator_picture[i].setPixmap(QtGui.QPixmap("icon/elevator.png"))
            self.elevator_picture[i].setGeometry(QtCore.QRect((20+60*(i-1))*1.5,565*1.5, 30*1.5, 30*1.5))
            self.elevator_picture[i].setScaledContents(True)

        #顶部显示
        self.location_label = {}
        for i in range(1, 6):
            self.location_label[i] = QtWidgets.QLabel(MainWindow)
            self.location_label[i].setText("1")
            self.location_label[i].setGeometry(QtCore.QRect((20+60*(i-1))*1.5,10*1.5, 40*1.5, 40*1.5))
            font = QtGui.QFont()
            font.setFamily("SimHei")
            font.setPointSize(25)
            self.location_label[i].setFont(font)
            self.location_label[i].setStyleSheet("color: rgb(200, 200, 0);")
            self.location_label[i].setTextFormat(QtCore.Qt.AutoText)

        #楼层标注
        self.floor_label={}
        for i in range(1, 21):
            self.floor_label[i] = QtWidgets.QLabel(MainWindow)
            self.floor_label[i].setText(str(i)+"F")
            self.floor_label[i].setGeometry(QtCore.QRect(60*6.3*1.5,(565-(i-1)*27)*1.5, 30*1.5, 30*1.5))
            font_floor = QtGui.QFont()
            font_floor.setFamily("SimSun")
            font_floor.setPointSize(17)
            font_floor.setBold(True)
            self.floor_label[i].setFont(font_floor)
            self.floor_label[i].setStyleSheet("color: rgb(150, 150, 200);")

        #电梯标注
        self.elevator_Label={}
        for i in range(1, 6):
            self.elevator_Label[i] = QtWidgets.QLabel(MainWindow)
            self.elevator_Label[i].setText(str(i))
            self.elevator_Label[i].setGeometry(QtCore.QRect(620*1.5,(10+120*(i-1))*1.5, 30*1.5, 30*1.5))
            font_elevator = QtGui.QFont()
            font_floor.setPointSize(20)
            font_floor.setBold(True)
            self.elevator_Label[i].setFont(font_floor)
            self.elevator_Label[i].setStyleSheet("color: rgb(255, 100, 100);")                            

        #电梯动画
        self.elevator_Anim = {}
        for i in range(1, 6):
            self.elevator_Anim[i] = QtCore.QPropertyAnimation(self.elevator_picture[i], b"geometry")

        self.up_btn = {}#上行按钮
        for i in range(1, 20):
            self.up_btn[i] = QtWidgets.QPushButton(MainWindow)  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.up_btn[i].setGeometry(QtCore.QRect(60*5*1.5,(565-(i-1)*27)*1.5, 30*1.5, 30*1.5))
            self.up_btn[i].setStyleSheet(self.upbtn_style)

        self.down_btn = {}#下行按钮
        for i in range(2, 21):
            self.down_btn[i] = QtWidgets.QPushButton(MainWindow)  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.down_btn[i].setGeometry(QtCore.QRect((60*5+30)*1.5,(565-(i-1)*27)*1.5,30*1.5,30*1.5))
            self.down_btn[i].setStyleSheet(self.downbtn_style)

        self.open_btn = {}#打开按钮
        for i in range(1, 6):
            self.open_btn[i] = QtWidgets.QPushButton(MainWindow)  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.open_btn[i].setGeometry(QtCore.QRect((470-26)*1.5,(120*(i-1)+10+26)*1.5,30*1.5,30*1.5))
            self.open_btn[i].setStyleSheet(self.openbtn_style)

        self.close_btn = {}#关闭按钮
        for i in range(1, 6):
            self.close_btn[i] = QtWidgets.QPushButton(MainWindow)  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.close_btn[i].setGeometry(QtCore.QRect((470-26)*1.5,(120*(i-1)+10+26+26)*1.5,30*1.5,30*1.5))
            self.close_btn[i].setStyleSheet(self.closebtn_style)

        self.alert_btn = {}#关闭按钮
        for i in range(1, 6):
            self.alert_btn[i] = QtWidgets.QPushButton(MainWindow)  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.alert_btn[i].setGeometry(QtCore.QRect((480+5*26)*1.5,(120*(i-1)+10+13+26)*1.5,30*1.5,30*1.5))
            self.alert_btn[i].setStyleSheet(self.alertbtn_style)

        self.number_btn = [[]for i in range(6)]  # 为使索引序号与电梯序号对应起来，创建六个子数组，第0个不加操作
        for i in range(1, 6):
            self.number_btn[i].append(0)  # 为使索引序号与电梯楼层对应起来，在第0个位置添加空项，用0替代
            for j in range(1, 21):
                self.number_btn[i].append(QtWidgets.QPushButton(MainWindow))  # 创建一个按钮，并将按钮加入到窗口MainWindow中
                self.number_btn[i][j].setGeometry(QtCore.QRect((470+(j-1)%5*26)*1.5,(120*(i-1)+10+(j-1)//5*26)*1.5,30*1.5,30*1.5))
                self.number_btn[i][j].setStyleSheet(
                    "QPushButton{border-image: url(icon/"+str(j)+"_hover.png)}"
                    "QPushButton:hover{border-image: url(icon/"+str(j)+".png)}"
                    "QPushButton:pressed{border-image: url(icon/"+str(j)+"_pressed.png)}"
                    )

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "anim"))


class myWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(myWindow, self).__init__()
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.schedul = elevator_schedul(self.ui)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = myWindow()
    application.show()
    sys.exit(app.exec_())
