# coding=utf-8
# Copyright (c) 2022 Q.Huang all rights reserved.
import numpy as np
import matplotlib.pyplot as plt
from numba import jit
from scipy.ndimage import label as CCL
import sys
sys.setrecursionlimit(1500)

MapL = 19           # 棋盘大小
step = 0            # 步数，为偶数时黑方落子
steps = []          # 每一步的坐标
ko = [0,-1,-1]      # 打劫标志 [flag,x,y]
end_flag = 0        # 游戏结束标志 1:虚着一次 2:黑胜 3: 白胜
mode = -1           # 模式: 0:双人, 1:我方执白, 2:我方执黑, 3:电脑-电脑
board = np.zeros((MapL,MapL),dtype=np.int16) # 生成棋盘
resolution = 768    # 默认棋盘大小

def GetArea(board):
    '''计算黑棋和白棋占领的面积'''
    area = [np.sum(board == 1),np.sum(board == 2)]
    chess = np.where(board != 0)
    zeros = np.where(board == 0)
    for i in range(len(zeros[0])):
        index = np.argmin(np.abs(chess[0]-zeros[0][i])+np.abs(chess[1]-zeros[1][i]))
        area[board[chess[0][index]][chess[1][index]]-1] += 1
    return area

def CalcScore(board,y=3,x=3):
    score = 0
    for n, player in enumerate([1+step%2, 2-step%2]): # n=0:mine,n=1:oppo 
        board_0 = board.copy()
        board_0[board_0 != player] = 0
        board_0[board_0 > 0] = 1
        components = CCL(board_0)[0]
        for i in range(int(np.max(components))):
            component = np.where(components==i+1)
            qi = CalcQi(component, board)          # 气
            count = len(component[0])              # 棋子数
            score += (1.1-2.1*n)*qi
            if count > 6 and qi < 2 and not n: 
                score -= 1000
            if qi < 4: score += (2*n-1) * (3.2-qi) * (0.7+count/(3+n*10)-n*0.3)
        score += (2*n-1) * (np.max(components)*2.1 - np.sum(board==player)*1.3)
    neighbor1 = board[max(y-2,0):min(y+1,MapL-1),max(x-2,0):min(x+1,MapL-1)]
    count = -1 + np.sum(neighbor1==1+step%2) - np.sum(neighbor1==2-step%2)
    score -= 0.01*abs(count)
    if abs(count) > 3: score -= 1
    if abs(count) > 5: score -= 500
    neighbor2 = board[max(y-3,0):min(y+2,MapL-1),max(x-3,0):min(x+2,MapL-1)]
    count = -1 + np.sum(neighbor2==1+step%2) - np.sum(neighbor2==2-step%2)
    score -= 0.02*abs(count)/(1+step/50)
    if abs(count) > 6: score -= 500
    score += 0.05/(min(abs(y-3.3),abs(y-MapL+3.3))+min(abs(x-3.3),abs(x-MapL+3.3)))/(1+step/40) 
    return score

def auto(player=2):
    '''电脑计算下一步棋的最佳位置'''
    # print("auto",end=' ')
    global ko
    max_score = -np.inf
    tizimax = [0,0]
    ymax = 1; xmax = 1
    # print("")
    score_start = CalcScore(board)
    for i in range(MapL):
        for j in range(MapL):
            if not board[i][j]:               
                temp = board.copy()
                # for r in range(np.random.randint(4)): np.rot90(temp)
                temp[i][j] = player
                tizis = tizi(temp)
                if not tizis[1] and tizis[0]:
                    temp[i][j] = 0
                    score = -9999
                elif ko[0] and abs(j-ko[1]+1) + abs(i-ko[2]+1) == 1:
                    temp[i][j] = 0
                    temp[ko[2]-1][ko[1]-1] = 2 - step%2
                    score = -9999
                else: score = CalcScore(temp,i+1,j+1) + np.random.rand()*0.01
                # print('%5.1d' % score,end='')
                if max_score < score:    
                    max_score = score; ymax = i+1; xmax = j+1; tizimax = tizis
            else: pass
                # print('  ['+'%s'%chr(21*board[i][j]+45)+']',end='')
        # print("")
    if tizimax == [1, 1]: ko = [1,xmax,ymax]
    else: ko = [0,-1,-1]
    if max_score - score_start < -500: 
        space(1)
        return -32,-32
    # print("max_score:",int(max_score),"(x,y):",xmax,ymax)
    return ymax, xmax
         
def button(event):
    '''选择游戏模式、启动控制'''
    # print("button",end=' ')
    if end_flag < 2:
        try:
            if mode == 0:
                move(round(event.ydata),round(event.xdata))
            elif mode == 1:
                if not step % 2: y,x = auto(1); move(y,x) # auto(1-Black 2-White）
                else: board = move(round(event.ydata),round(event.xdata))    
            elif mode == 2:
                if not step % 2: move(round(event.ydata),round(event.xdata))
                else: y,x = auto(2); move(y,x)   
            elif mode == 3:
                if not step % 2: y,x = auto(1); move(y,x)
                else: y,x = auto(2); move(y,x)
        except: pass
            
def space(event):
    '''按空格键虚着，按Q退出程序'''
    # print("space",end=' ')
    global step, end_flag
    if event == 1 or event.key == " ":
        print("白" if step%2 else "黑","方虚着")
        step += 1
        end_flag += 1        # 1次虚着准备
        print("end_flag:",end_flag)
        steps.append([-32,-32])
        show()
        if mode & (step % 2 + 1): button(1)
    
def move(y,x):
    '''走一步棋'''
    # print("move",end=' ')
    global step,ko,end_flag
    i, j = y-1, x-1
    try:
        if not board[i][j]: 
            board[i][j] = step%2 + 1
            tizis = tizi(board)
            # 判断是否有气
            if not tizis[1] and tizis[0]:
                board[i][j] = 0
                print("无气。不能在此落子。")
                raise Exception("0")
            # 判断是否劫争
            elif ko[0] and abs(x-ko[1]) + abs(y-ko[2]) == 1:
                board[i][j] = 0
                board[ko[2]-1][ko[1]-1] = 2 - step%2
                print("劫争。不能在此落子。")
                raise Exception("1")
            if tizis[0] == 1 and tizis[1] == 1:
                ko = [1,x,y]
            else: ko = [0,-1,-1]
            
            step += 1
            steps.append([y,x])
            end_flag = 0
            
            show() 
            if mode & (step % 2 + 1): button(1)       
    except: pass
    
@jit
def CalcQi(component, board):
    '''计算一块棋的气'''
    qi = 0    
    zeros = np.where(board == 0)   
    for n in range(len(zeros[0])):
        i,j = zeros[0][n], zeros[1][n]
        if i < np.min(component[0])-1 or i > np.max(component[0])+1: continue
        if j < np.min(component[1])-1 or j > np.max(component[1])+1: continue
        exit_flag = 0
        for offset in [[0, -1], [-1, 0], [1, 0], [0, 1]]:
            i2, j2 = i + offset[0], j + offset[1]
            if 0 <= i2 < MapL and 0 <= j2 < MapL:
                for m in range(len(component[0])):
                    if i2 == component[0][m] and component[1][m] == j2:
                        qi += 1
                        if (min(i,j)==0 or max(i,j)==MapL) and (min(i2,j2)==0 or max(i2,j2)==MapL): qi += 0.2
                        exit_flag = True
                        break
            if exit_flag: break                
    return qi

def tizi(board):
    '''提子，返回提子的数量'''
    #print("tizi")
    tizi_nums = [0,0]
    board_0 = board.copy()
    for n, player in enumerate([1+step%2, 2-step%2]):
        board_1 = board_0.copy()
        board_1[board_1 != player] = 0
        board_1[board_1 > 0] = 1
        components = CCL(board_1)[0]
        for i in range(int(np.max(components))):
            component = np.where(components==i+1)
            if CalcQi(component, board) == 0: 
                tizi_nums[n] += np.shape(component)[1]
                if n: board[component] = 0
    return tizi_nums
        
def show():
    '''显示棋盘'''
    # print("show")
    colors = [0, 'k','w']
    names = ['player','PC']
    adsize = 0 if mode == 3 else step % 2
    
    if end_flag < 2: plt.clf()
    fig = plt.figure(num=1)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(0+adsize,30,resolution+adsize-30,resolution-30) # position of figures
    fig.canvas.mpl_connect('button_press_event', button)
    fig.canvas.mpl_connect("key_press_event", space)
    plt.xlim(0.5, MapL+0.5)
    plt.ylim(0.5, MapL+0.5)
    for i in range(MapL):
        for j in range(MapL):
            if board[i][j]:
                plt.scatter(j+1,i+1,
                            c=colors[board[i][j]],s=resolution*8/(MapL-1),
                            linewidths=1,edgecolors='k',zorder=32)
    if step:
        plt.scatter(steps[-1][1],steps[-1][0],s=int(resolution/10),c='r',lw=5,marker='+',zorder=64)
    plt.scatter([4,4,4,10,10,10,16,16,16],[4,10,16,4,10,16,4,10,16],c='k',s=int(resolution/60),zorder=2)
    plt.plot([1,1,MapL,MapL,1],[1,MapL,MapL,1,1],c='k',lw=1.5)
    plt.fill([1,MapL,MapL,1],[1,1,MapL,MapL],c='tan',alpha=1,zorder=0)
    plt.fill([-1,MapL+1,MapL+1,-1],[-1,-1,1+MapL,1+MapL],c='tan',alpha=0.4,zorder=1)
    plt.grid(True,c='k',zorder=1)
    plt.text(MapL/2+0.5,MapL+1.5,"Step:"+str(step)+"  Black:"+names[mode & 1]+"  White:"+names[(mode&2)//2],
             fontsize=15,horizontalalignment="center")

    ax = plt.gca()
    ax.set_xticks(range(1,MapL+1))
    ax.set_yticks(range(1,MapL+1)) 
    for edge in ['left','right','top','bottom']:
        ax.spines[edge].set_visible(False)
    if end_flag == 2:
        area = GetArea(board)
        string = "Black: "+str(area[0])+"   White: "+str(area[1])
        plt.text(MapL/2+0.5,MapL+0.8,string,fontsize=20,c='r',
                 verticalalignment="center", horizontalalignment="center")
    
    if mode & (step % 2 + 1): 
        if not step: plt.pause(0.01)
        fig.canvas.draw_idle()
        fig.canvas.start_event_loop(0.1)
        if end_flag < 2: plt.clf()  
        else: plt.pause(60)
    else:  
        plt.show()

#获取屏幕分辨率    
try:
    from win32 import win32gui, win32print
    from win32.lib import win32con
    def get_resolution():
        '''获取windows屏幕分辨率'''
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
        return min(w,h)
    resolution = get_resolution()
except: 
    resolution = 730
    print("获取屏幕分辨率失败，设置为默认值")

if __name__ == "__main__":

    print('#'*6+"\n 围棋\n"+'#'*6+"\n描述：单击棋盘开始，点击棋盘落子，按空格键虚着，关闭棋盘刷新/开始新的一局。\n")
    while mode not in [0, 1, 2, 3, 4]:
        mode = int(input("选择模式（0:双人模式，1:我方执白, 2:我方执黑, 3:电脑-电脑，Q:退出）\n请输入："))
    print("加载中……")
    while end_flag < 2:
        show()
        if mode & (step % 2 + 1): button(1)
