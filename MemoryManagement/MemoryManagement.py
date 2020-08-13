import random

class MemoryManagementCore:
    def __init__(self):
        self.blockPage=[[-1 for i in range(4)] for i in range(2)]#用于存放当前在物理内存中的页号
        self.blockFIFOQueue=[-1]*320#FIFO算法所需要使用的队列
        self.queueHead=0#队列头部
        self.queueCurrent=0#队列尾部
        self.blockLRUSignal=[0]*4#LRU算法所需的列表
        self.pageNumber=[0]*2#存放总的页数
        self.pageFaultNumber=[0]*2#存放缺页数
        self.pageStaus1=[]#存放缺页命中情况
        self.pageStaus2=[]


    def algorithmFIFO(self,newPage):#FIFO算法
        for i in range(4):
            if self.blockPage[0][i]==-1:#首先判断是否为放入任何块
                self.blockPage[0][i]=newPage#放入新页
                self.blockFIFOQueue[self.queueCurrent]=i#调整队列
                self.queueCurrent+=1
                self.pageFaultNumber[0]+=1
                self.pageNumber[0]+=1
                self.pageStaus1.append('Block'+str(i+1)+' Miss')
                return
            elif self.blockPage[0][i]==newPage:#命中情况
                self.pageNumber[0]+=1
                self.pageStaus1.append('Block'+str(i+1)+' Hit')
                return
        replaceBlock= self.blockFIFOQueue[self.queueHead]#没有命中，取出队列头部
        self.queueHead+=1
        self.blockPage[0][replaceBlock]=newPage#放入新页
        self.blockFIFOQueue[self.queueCurrent]=replaceBlock#调整队列
        self.queueCurrent+=1
        self.pageFaultNumber[0]+=1
        self.pageNumber[0]+=1
        self.pageStaus1.append('Block'+str(replaceBlock+1)+' Miss')

    def algorithmLRU(self,newPage):#LRU算法
        for i in range(4):
            if self.blockPage[1][i]==-1:#首先判断是否为放入任何块
                self.blockPage[1][i]=newPage#放入新页
                for j in range(4):#对于没有访问的块+1，表示时间+1
                    self.blockLRUSignal[j]+=1
                self.blockLRUSignal[i]=0
                self.pageNumber[1]+=1
                self.pageFaultNumber[1]+=1
                self.pageStaus2.append('Block'+str(i+1)+' Miss')
                return
            elif self.blockPage[1][i]==newPage:#命中情况
                for j in range(4):
                    self.blockLRUSignal[j]+=1
                self.blockLRUSignal[i]=0
                self.pageNumber[1]+=1
                self.pageStaus2.append('Block'+str(i+1)+' Hit')
                return
        replaceBlock= self.blockLRUSignal.index(max(self.blockLRUSignal))#没有命中，取出时间状态最大的
        self.blockPage[1][replaceBlock]=newPage#放入新页
        for j in range(4):#对于没有访问的块+1，表示时间+1
            self.blockLRUSignal[j]+=1
        self.blockLRUSignal[replaceBlock]=0
        self.pageFaultNumber[1]+=1
        self.pageNumber[1]+=1
        self.pageStaus2.append('Block'+str(replaceBlock+1)+' Miss')


def generateInstructions():#用于产生队列，50%顺序，25%前址，25%后址
    m = random.randint(1, 318)
    i=1
    instructions = []
    pages = []
    instructions.append(m)#找到第一个随机数
    pages.append(m//10)
    instructions.append(m + 1)
    pages.append((m + 1)//10)
    while len(instructions) <= 318:#产生320条
        if m-60>=0:#产生的范围在前后60条指令内以此模拟程序局部性原理
            m1 = random.randint(m-60, m - 1)
        else:
            m1 = random.randint(0, m - 1)
        instructions.append(m1)
        instructions.append(m1 + 1)
        pages.append(m1//10)
        pages.append((m1 + 1) // 10)
        if m1+60<=318:#产生的范围在前后60条指令内以此模拟程序局部性原理
            m2 = random.randint(m1 + 2, m1+60)
        else:
            m2 = random.randint(m1 + 2, 318)
        instructions.append(m2)
        instructions.append(m2 + 1)
        pages.append(m2 // 10)
        pages.append((m2 + 1) // 10)
        m = m2
    return instructions,pages