import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from mainUI import*
import math
import pickle


class FAT(object):
    def __init__(self):
        self.bitMap = [-2 for i in range(1024 * 2)]#位示图结合显示连接

class FCB(object):#文件控制表
    def __init__(self, name, path, address, size, type):
        self.name = name#文件名
        self.path = path#父节点的路径
        self.address = address  #第一块内容在位示图中的位置
        self.size = size  # 文本文件内容大小
        self.type = type  # 文件类型
        self.child = {}  #文件的子节点的路径


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow,self).__init__()
        self.setupUi(self)
        self.myFAT=FAT()#初始化
        self.FCBlist = {'Root': FCB('Root', '', '', '', 'folder')}#用于存放FCB的列表，路径索引
        self.storageContent = {}  # 代表磁盘文件的内容，路径索引
        self.importStorage()  # 导入上次运行之后保存的内容
        self.treeWidget.itemClicked.connect(self.updatePath)#绑定按钮
        self.pushButton_3.clicked.connect(self.openFile)
        self.pushButton_5.clicked.connect(self.createText)
        self.pushButton_4.clicked.connect(self.createFolder)
        self.pushButton_2.clicked.connect(self.deleteItem)
        self.pushButton_9.clicked.connect(self.closeUI)
        self.pushButton.clicked.connect(self.formatStorage)
        self.treeWidget.expandAll()  # 节点全部展开
     
         
    def updatePath(self):  # 更新路径显示
        path = self.getPath()
        self.label.setText("当前路径:"+ path )

    def createText(self):#创建文本文件
        path = self.getPath()#获取路径
        if path==False or self.FCBlist[path].type == 'file':#判断是否是文件
            return False
        name, isSuccess = QtWidgets.QInputDialog.getText(self, "name", "请输入名称", QtWidgets.QLineEdit.Normal, '')#对话框输入
        if name == '':#判断输入名字是否正确
            return False
        currentFolder = self.treeWidget.currentItem()
        childNode = currentFolder.takeChildren()
        if self.isRepeat(childNode,"file",path,name,currentFolder):
            return False
        text, isSuccess = QtWidgets.QInputDialog.getMultiLineText(self, "file", '请输入文本内容', '')#对话框输入内容
        address = self.fillBlock(len(text))#填入位示图
        if address == -1:#判断是否有空间
            currentFolder.addChildren(childNode)
            return False
        currentFolder.addChildren(childNode)
        self.addNode(name+'.txt',currentFolder)#加入树节点
        insertFCB = FCB(name + '.txt', path, address, len(text), 'file')#修改插入FCB
        currentPath = path + '\\' + name + '.txt'
        self.FCBlist[currentPath] = insertFCB
        self.storageContent[currentPath] = text
        self.FCBlist[path].child[currentPath] = insertFCB
        self.treeWidget.expandAll()

    def createFolder(self):#创建目录
        path = self.getPath()#获取路径
        if path==False or self.FCBlist[path].type == 'file':#判断是否是文件目录
            return False
        name, isSuccess = QtWidgets.QInputDialog.getText(self, "name", "请输入名称", QtWidgets.QLineEdit.Normal, '')#输入文件名称
        currentFolder = self.treeWidget.currentItem()
        childNode = currentFolder.takeChildren()
        if self.isRepeat(childNode,"folder",path,name,currentFolder):
            return False
        currentFolder.addChildren(childNode)
        if name == '':
            return False
        self.addNode(name,currentFolder)#加入树节点
        path = self.getPath()
        currentFCB = FCB(name, path, '', '', 'folder')#修改插入FCB
        fullPath = path + '\\' + name
        self.FCBlist[fullPath] = currentFCB
        self.FCBlist[path].child[fullPath] = currentFCB
        self.treeWidget.expandAll() 

    def isRepeat(self,childNode,type,path,name,currentFolder):
        if type=='file':
            name=name+'.txt'
        for i in childNode:#判断是否重名
            childPath=path+'\\'+ i.text(0)
            if i.text(0) == name and self.FCBlist[childPath].type == type:
                currentFolder.addChildren(childNode)
                return True

    def addNode(self,name,currentNode):#插入节点
        child = QtWidgets.QTreeWidgetItem()#设置属性
        child.setText(0, name)
        font = QtGui.QFont()
        font.setPointSize(12)
        child.setFont(0, font)
        currentNode.addChild(child)#加入节点
        return child

    def fillBlock(self, size): #填充位示图
        if size != 0:#向上取整
            blockNum = math.ceil(size / 512)
        else:
            blockNum = 1
        address=-1#首地址
        currentNum = 0
        temp=0
        for i in range(2048):  # 遍历位示图
            if self.myFAT.bitMap[i] < -1:  # 判断空闲块
                self.myFAT.bitMap[i] = -1  # 末尾标注作为显示链接的结尾
                if currentNum > 0:
                    self.myFAT.bitMap[temp] = i#显示链接的记录
                else:
                    address = i
                currentNum += 1
                temp=i
                if currentNum == blockNum:#判断是否出错
                    break
        return address

    def getPath(self):  # 获取当前目录项
        item = self.treeWidget.currentItem()#获取当前树节点
        if item:
            path = item.text(0)
            fatherPath = item.parent()
            while fatherPath:#循环查找到根节点
                path = fatherPath.text(0) + '\\' + path#转化为路径
                fatherPath = fatherPath.parent()
            return path
        else:
            return False

    def deleteItem(self):#删除选中项
        path = self.getPath()#获取路径
        item = self.treeWidget.currentItem()
        if item:
            if path == 'Root':
                return False
            if self.FCBlist[path].type == 'file':#删除文本或者文件目录
                self.deleteText(item, path)
            else:
                self.deleteFolder(item, path)

    def deleteText(self, textNode, path):#删除文本文件
        currentFCB = self.FCBlist[path]
        fileHead = currentFCB.address
        next = self.myFAT.bitMap[fileHead]
        self.myFAT.bitMap[fileHead] = -2
        while next != -1 and next >= 0:#位示图填充初始状态
            prev = next
            next = self.myFAT.bitMap[next]
            self.myFAT.bitMap[prev] = -2
        self.deleteFCB(path)#删除节点
        self.storageContent.pop(path)
        parentNode = textNode.parent()
        if parentNode:
            parentNode.removeChild(textNode)
        self.treeWidget.expandAll()

    def deleteFolder(self, folderNode, path):#删除文件目录
        childNode = folderNode.takeChildren()
        if len(childNode) == 0:
            if path in self.FCBlist:
                self.deleteFCB(path)
                parentNode = folderNode.parent()
                if parentNode:
                    parentNode.removeChild(folderNode)
            return
        for child in childNode:#对于每个子节点
            name = child.text(0)
            childPath = path + '\\' + name
            if self.FCBlist[childPath].type == 'file':
                self.deleteText(child, childPath)
            else:
                self.deleteFolder(child, childPath)
        if path!='Root':#除根节点外的操作
            parentNode = folderNode.parent()
            if parentNode:
                parentNode.removeChild(folderNode)
            self.deleteFCB(path)

    def deleteFCB(self,path):#删除FCB
        parentPath = self.FCBlist[path].path
        if parentPath!='':
            self.FCBlist[parentPath].child.pop(path)
            self.FCBlist.pop(path)
        else:
            return

    def formatStorage(self):#格式化
        self.deleteFolder(self.item_0,'Root')


    def openFile(self):  # 读写文件内容
        path = self.getPath()
        if path==False or self.FCBlist[path].type == 'folder':
            return False
        currentText = self.storageContent[path]
        inputText, isSuccess = QtWidgets.QInputDialog.getMultiLineText(self, "File", '请输入文本内容', currentText)#获取文本
        if isSuccess:
            self.storageContent[path] = inputText
            newNum = math.ceil(len(inputText)/512)
            oldNum = math.ceil(self.FCBlist[path].size/512)
            currentFCB = self.FCBlist[path]
            if newNum > oldNum:#如果新块大于旧块  
                shortage = newNum - oldNum
                fileHead = currentFCB.address
                next = self.myFAT.bitMap[fileHead]
                pre = fileHead
                while next != -1 and next >= 0:#找到链接尾部
                    pre = next
                    next = self.myFAT.bitMap[next]
                address = self.fillBlock(len(inputText)+(self.FCBlist[path].size % 512)-512-self.FCBlist[path].size)#添加块
                self.myFAT.bitMap[pre] = address
                self.FCBlist[path].size = len(inputText)
            elif newNum < oldNum:#如果新块小于旧块 
                abound = oldNum - newNum  
                fileHead = currentFCB.address
                next = self.myFAT.bitMap[fileHead]
                pre = fileHead
                par = {next: pre}
                while next != -1 and next >= 0:#找到尾部
                    pre = next
                    next = self.myFAT.bitMap[next]
                    par[next] = pre
                eliminateBit = par[next]
                for i in range(abound):#回溯复原块
                    self.myFAT.bitMap[eliminateBit] = -2
                    if eliminateBit in par:
                        eliminateBit = par[eliminateBit]
                if newNum == 0:
                    self.myFAT.bitMap[eliminateBit] = -2
                else:
                    self.myFAT.bitMap[eliminateBit] = -1
                self.FCBlist[path].size = len(inputText)

    def storeFile(self):#存入二进制文件
        fileFCB=open('fileFCB.bin','wb')
        pickle.dump(self.FCBlist,fileFCB)
        fileFCB.close()
        fileFAT=open('fileFAT.bin','wb')
        pickle.dump(self.myFAT.bitMap,fileFAT)
        fileFAT.close()
        fileCNT=open('fileCNT.bin','wb')
        pickle.dump(self.storageContent,fileCNT)
        fileCNT.close()


    def importStorage(self):#从二进制文件中读出
        fileFCB=open('fileFCB.bin','rb')
        self.FCBlist=pickle.load(fileFCB)
        fileFCB.close()
        fileFAT=open('fileFAT.bin','rb')
        self.myFAT.bitMap=pickle.load(fileFAT)
        fileFAT.close()
        fileCNT=open('fileCNT.bin','rb')
        self.storageContent=pickle.load(fileCNT)
        fileCNT.close()
        self.createTree('Root',self.item_0)

    def createTree(self,path,parentNode):#递归的构造目录树
        for i in self.FCBlist[path].child:
            item=self.addNode(self.FCBlist[i].name,parentNode)
            self.createTree(i,item)

    def closeUI(self, event):#保存文档并退出
        self.storeFile()
        self.close()


if __name__ == '__main__':
  app = QApplication(sys.argv)
  #实例化主窗口 
  main = MyMainWindow()
   
  #显示
  main.show()
  sys.exit(app.exec_())

