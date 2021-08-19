# Copyright (c) 2021 Q.Huang all rights reserved.
import numpy as np
import matplotlib.pyplot as plt

MapL = 15    # Chessboard size
WinN = 5     # "Five"-in-a-row
step = 0     # Steps taken
steps = []   # Coordinates of each step
end_flag = 0 # Game end flag
board = np.zeros((MapL,MapL),dtype=np.int) # chessboard

mode = 2     # modes: 0:player-player, 1:PC-player, 2:player-PC, 3:PC-PC

# parameters           1  2   3   4   5   6    7    8    9   10  11   12    13    14    15    16    17    18    19    20    
coeffs = [np.array([[-12, 0,-35,-15,-34,-25,-1000,-60,-1000,-30,-30,-100, -9999,-9999,-9999,-9999,-9999,-9999,-9999,-99999],
                    [ 10, 3, 30, 15, 29, 12,  190, 70, 180,  20, 20, 4000,  140,  135,  130, 130,  200,  135,  135, 99999]]),
          
          np.array([[-15,-3,-40,-15,-35,-25,-1500,-75,-1500,-40,-30,-1050, -9000,-9000,-9000,-9000,-9000,-9000,-9000,-90000],
                    [ 10, 3, 30, 15, 29, 12,  190, 70,  180, 20, 20, 4000,   140,  130,  130,  130,  200,  125, 135, 90000]])]
numsall = np.zeros((2,len(coeffs[0][0])))

def judge(l,c,winn):
    '''judge if a player wins by taking a move (l,c)'''
    # line #
    count = 0
    i = 0
    while i < MapL-1 and count < WinN-1:
        if board[l][i] and board[l][i] == board[l][i+1]:
            count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # column #
    count = 0
    i = 0
    while i < MapL-1 and count < WinN-1:
        if board[i][c] and board[i][c] == board[i+1][c]:
            count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # Principal diagonal #
    count = 0
    i = 0
    l_ = l - min(l,c); c_ = c - min(l,c)
    while i+l_<MapL-1 and i+c_<MapL-1 and count<WinN-1:
        if board[i+l_][i+c_] and board[i+l_+1][i+c_+1] == board[i+l_][i+c_]:
            count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # Subdiagonal #
    count = 0
    i = 0	
    while c > 0 and l < MapL-1:
        l += 1; c -= 1
    while l-i>0 and i+c<MapL and count<WinN-1:
        if board[-i+l][i+c] and board[-i+l-1][i+c+1] == board[-i+l][i+c]:
            count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1

    return 0

def auto(player=2,old=False):
    '''computer's move'''
    global numsall
    max_score = -np.inf
    ymax = 1; xmax = 1
    coeff = 1 if old else 0
    print("\nWaiting ... ... next step:",step+1)
    # Calculate the score at each point
    for y in range(MapL):
        for x in range(MapL):
            if not board[y][x]:
                cd = abs(y-MapL/2+0.5) + abs(x-MapL/2+0.5)
                if (step and not np.any(board[max(y-2,0):min(y+3,MapL),max(x-2,0):min(x+3,MapL)])) or (not step and cd>5):
                    score = -np.inf
    #                print("     ",end='')
                else:
                    board[y][x] = player
                    score = score_calc(coeffs[coeff],player)-cd+np.random.randint(-3,4)
                    board[y][x] = 3-player
                    score2 = score_calc(coeffs[coeff],player)
                    if 1.5<score2/coeffs[coeff][0][6]<2.5 or 0.5<(score2-coeffs[coeff][0][12])/coeffs[coeff][0][6]<1.5:
                        score -= coeffs[coeff][0][6]/2
                    if 1.9<score2/coeffs[coeff][0][12]<2.1:
                        score -= coeffs[coeff][0][6]/2
    #                print('%5d' % score,end='')
                    if max_score < score:
                        max_score = score; ymax = y+1; xmax = x+1
                    board[y][x] = 0
    #        else:
    #            print('  ['+'%s'%chr(21*board[y][x]+45)+']',end='')
    #    print("")
    #print("B:",end='')
    #for j in range(len(numsall[0])): print('%2d'%int(numsall[0][j]),end=' ')
    #print("\nW:",end='')
    #for j in range(len(numsall[0])): print('%2d'%int(numsall[1][j]),end=' ')
    #print("")
    return ymax,xmax

def score_calc(coeff,player=2):
    
    nums = np.zeros((2,len(coeffs[0][0])))
    def one_calc(a):
        '''calculate each list'''
        l = len(a)
        a = a.tolist()
        if l>=3:
            for i in range(l-2):
                if a[i:i+3]==[0,1,0]: nums[0][0]+=1
                if a[i:i+3]==[2,1,0] or a[i:i+3]==[0,1,2]: nums[0][1]+=1
                    
                if a[i:i+3]==[0,2,0]: nums[1][0]+=1
                if a[i:i+3]==[1,2,0] or a[i:i+3]==[0,2,1]: nums[1][1]+=1
        if l>=4:
            for i in range(l-3):
                if a[i:i+4]==[0,1,1,0]: nums[0][2]+=1
                if a[i:i+4]==[2,1,1,0] or a[i:i+4]==[0,1,1,2]: nums[0][3]+=1
                    
                if a[i:i+4]==[0,2,2,0]: nums[1][2]+=1
                if a[i:i+4]==[1,2,2,0] or a[i:i+4]==[0,2,2,1]: nums[1][3]+=1
        if l>=5:
            for i in range(l-4):
                if a[i:i+5]==[0,1,0,1,0]: nums[0][4]+=1
                if a[i:i+5]==[0,1,0,1,2] or a[i:i+5]==[2,1,0,1,0]: nums[0][5]+=1
                if a[i:i+5]==[0,1,1,1,0]: nums[0][6]+=1
                if a[i:i+5]==[0,1,1,1,2] or a[i:i+5]==[2,1,1,1,0]: nums[0][7]+=1
                if a[i:i+5]==[1,1,1,1,1]: nums[0][-1]+=1
                    
                if a[i:i+5]==[0,2,0,2,0]: nums[1][4]+=1
                if a[i:i+5]==[0,2,0,2,1] or a[i:i+5]==[1,2,0,2,0]: nums[1][5]+=1
                if a[i:i+5]==[0,2,2,2,0]: nums[1][6]+=1
                if a[i:i+5]==[0,2,2,2,1] or a[i:i+5]==[1,2,2,2,0]: nums[1][7]+=1
                if a[i:i+5]==[2,2,2,2,2]: nums[1][-1]+=1
            if a[l-5:l]==[0,1,1,1,1] or a[0:5]==[1,1,1,1,0]: nums[0][18]+=1
            if a[l-5:l]==[1,1,0,1,1] or a[0:5]==[1,1,0,1,1]: nums[0][18]+=1
            if a[l-5:l]==[1,1,1,0,1] or a[0:5]==[1,1,1,0,1]: nums[0][18]+=1
            if a[l-5:l]==[1,0,1,1,1] or a[0:5]==[1,0,1,1,1]: nums[0][18]+=1
            if a[l-5:l]==[0,2,2,2,2] or a[0:5]==[2,2,2,2,0]: nums[1][18]+=1
            if a[l-5:l]==[2,2,0,2,2] or a[0:5]==[2,2,0,2,2]: nums[1][18]+=1
            if a[l-5:l]==[2,2,2,0,2] or a[0:5]==[2,2,2,0,2]: nums[1][18]+=1
            if a[l-5:l]==[2,0,2,2,2] or a[0:5]==[2,0,2,2,2]: nums[1][18]+=1
            
        if l>=6:
            for i in range(l-5):
                if a[i:i+6]==[0,1,0,1,1,0] or a[i:i+6]==[0,1,1,0,1,0]: nums[0][8]+=1
                if a[i:i+6]==[2,1,0,1,1,0] or a[i:i+6]==[0,1,1,0,1,2]: nums[0][9]+=1
                if a[i:i+6]==[2,1,1,0,1,0] or a[i:i+6]==[0,1,0,1,1,2]: nums[0][10]+=1
                if a[i:i+6]==[0,1,1,1,1,0]: nums[0][11]+=1
                if a[i:i+6]==[2,1,1,1,1,0] or a[i:i+6]==[0,1,1,1,1,2]: nums[0][12]+=1
                    
                if a[i:i+6]==[0,2,0,2,2,0] or a[i:i+6]==[0,2,2,0,2,0]: nums[1][8]+=1
                if a[i:i+6]==[1,2,0,2,2,0] or a[i:i+6]==[0,2,2,0,2,1]: nums[1][9]+=1
                if a[i:i+6]==[0,2,2,0,2,1] or a[i:i+6]==[0,2,0,2,2,1]: nums[1][10]+=1
                if a[i:i+6]==[0,2,2,2,2,0]: nums[1][11]+=1
                if a[i:i+6]==[1,2,2,2,2,0] or a[i:i+6]==[0,2,2,2,2,1]: nums[1][12]+=1
        if l>=7:
            for i in range(l-6):
                if a[i:i+7]==[2,1,1,0,1,1,2] or a[i:i+7]==[2,1,0,1,1,1,2] or a[i:i+7]==[2,1,1,1,0,1,2]: nums[0][13]+=1
                if a[i:i+7]==[2,1,1,0,1,1,0] or a[i:i+7]==[0,1,1,0,1,1,2]: nums[0][14]+=1
                if a[i:i+7]==[0,1,1,0,1,1,0] or a[i:i+7]==[0,1,1,1,0,1,2] or a[i:i+7]==[2,1,0,1,1,1,0]: nums[0][15]+=1
                if a[i:i+7]==[0,1,1,1,0,1,0] or a[i:i+7]==[0,1,0,1,1,1,0]: nums[0][16]+=1
                if a[i:i+7]==[0,1,0,1,1,1,2] or a[i:i+7]==[2,1,1,1,0,1,0]: nums[0][17]+=1
                
                if a[i:i+7]==[1,2,2,0,2,2,1] or a[i:i+7]==[1,2,0,2,2,2,1] or a[i:i+7]==[1,2,2,2,0,2,1]: nums[1][13]+=1
                if a[i:i+7]==[1,2,2,0,2,2,0] or a[i:i+7]==[0,2,2,0,2,2,1]: nums[1][14]+=1
                if a[i:i+7]==[0,2,2,0,2,2,0] or a[i:i+7]==[0,2,2,2,0,2,1] or a[i:i+7]==[1,2,0,2,2,2,0]: nums[1][15]+=1
                if a[i:i+7]==[0,2,2,2,0,2,0] or a[i:i+7]==[0,2,0,2,2,2,0]: nums[1][16]+=1
                if a[i:i+7]==[0,2,0,2,2,2,1] or a[i:i+7]==[1,2,2,2,0,2,0]: nums[1][17]+=1
        
    for i in range(MapL):
        # Calculate row and column
        one_calc(board[i])
        one_calc(board[:,i])
    for i in range(-MapL+1,MapL):
        # Calculate the main and sub diagonals
        one_calc(np.diag(board,i))
        one_calc(np.diag(np.flip(board,axis=0),i))
        
    nums[:,0] -= nums[:,4]*2 + nums[:,8]+nums[:,10]+nums[:,16]+nums[:,17]
    nums[:,1] -= nums[:,5] + nums[:,9]
    nums[:,2] -= nums[:,8] + nums[:,9]+nums[:,14]+nums[:,15]
    nums[:,3] -= nums[:,10] + nums[:,14]
    nums[:,6] -= nums[:,15] + nums[:,16]
    nums[:,7] -= nums[:,17]
    
    global numsall
    numsall = nums
    if player==2: 
        return np.sum(nums*coeff)
    else:
        return np.sum(nums*np.flip(coeff,axis=0))
    
def button(event):
    '''event handler & modes'''
    if not end_flag:
        try:
            if mode == 0:
                move(round(event.ydata),round(event.xdata))
            elif mode == 1:
                if not step % 2: y,x = auto(1,1); move(y,x) # auto(1-B 2-W, 0-Old 1-New）
                else: move(round(event.ydata),round(event.xdata))    
            elif mode == 2:
                if not step % 2: move(round(event.ydata),round(event.xdata))
                else: y,x = auto(2,1); move(y,x)   
            elif mode == 3:
                if not step % 2: 
                    y,x = auto(1,1); move(y,x)
                else: 
                    y,x = auto(2,1); move(y,x)
        except: pass
    
def move(i,j):
    global step,board,end_flag
    label = [1,2]  
    try:
        if not board[i-1][j-1]: 
            board[i-1][j-1] = label[step%2]
            step += 1
            steps.append([i,j])
            if judge(i-1,j-1,WinN): end_flag = 1
            elif step == MapL**2: end_flag = 2
            show()
    except:
        return -1 

def show():
    '''show chessboard'''
    colors = ['w','k','whitesmoke']
    edge = ['left','right','top','bottom']
    edgex = [1,1,MapL,MapL,1]; edgey = [1,MapL,MapL,1,1]
    names = ['player','PC']
    adsize = 0 if mode == 3 else step % 2
    
    if not end_flag: plt.clf()
    fig = plt.figure(num=1)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(0+adsize,30,700+adsize,700) # position of figures
    fig.canvas.mpl_connect('button_press_event', button)
    plt.xlim(0.5,MapL+0.5)
    plt.ylim(0.5,MapL+0.5)
    for i in range(MapL):
        for j in range(MapL):
            if board[i][j]:
                plt.scatter(j+1,i+1,
                            c=colors[board[i][j]],s=520*12/(MapL-1),
                            linewidths=1,edgecolors='k',zorder=128)
    if step:
        plt.scatter(steps[-1][1],steps[-1][0],s=100,c='r',lw=5,marker='+',zorder=256)
    plt.plot(edgex,edgey,c='k',lw=1)
    plt.fill([1,MapL,MapL,1],[1,1,MapL,MapL],c='tan',alpha=0.5,zorder=0)
    plt.fill([-MapL,2*MapL,2*MapL,-MapL],[-MapL,-MapL,2*MapL,2*MapL],c='tan',alpha=0.3,zorder=1)
    plt.grid(True,ls='--',c='k',zorder=1)
    plt.text(MapL/2,MapL+1.5,"Step:"+str(step)+"  Black:"+names[mode & 1]+"  White:"+names[(mode&2)//2],
             fontsize=15,horizontalalignment="center")
    ax = plt.gca()
    ax.set_xticks(range(1,MapL+1))
    ax.set_yticks(range(1,MapL+1)) 
    for edg in edge:
        ax.spines[edg].set_visible(False)
    if end_flag:
        if end_flag == 2: 
            string = "Draw!"
        else: 
            string = "Black Wins" if step%2 else "White Wins"
        plt.text(MapL/2+0.5,MapL+0.5,string,fontsize=20,c='r',
                 verticalalignment="center",
                 horizontalalignment="center")
    
    if mode & (step % 2 + 1): 
        plt.ion()
        plt.pause(0.1)
        if not end_flag: plt.clf()
        button(1)
    else:  
        plt.ioff()
        plt.show()
        
                
if __name__ == "__main__":
    result = [0,0]
    print('#'*8+"\n Gobang\n"+'#'*8+"\nDescription: please click the chessboard in the order of playing chess. After each game, close the chessboard to start a new game. Set the players (PC/player) on line 12 of the code")
    while 1:
        show()
        if end_flag == 1:
            if step % 2: result[0] += 1
            else: result[1] += 1   
            end_flag = 0
            step = 0
            steps = []
            board[board != 0] = 0
            print("\n----- SCORE -----\nBlack",result[0],'-',result[1],"White\n"+"-"*17)    