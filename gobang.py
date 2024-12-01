# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt

MapL = 15     # Chessboard size
WinN = 5      # need "five"-in-a-row to win
step = 0      # Steps taken
steps = []    # Coordinates of each step
end_flag = 0  # Game end flag
board = np.zeros((MapL, MapL), dtype=np.int8) # chessboard

mode = 4     # modes: 0:player-player, 1:PC-player, 2:player-PC, 3:PC-PC

# parameters           1  2   3   4   5   6    7    8    9   10  11    12    13    14    15    16    17    18    19     20
coeffs = [np.array([[-12, 0,-35,-15,-34,-25,-1000,-45,-1000,-30,-30,-1000,-9500,-9500,-9500,-9500,-9500,-9500,-9500,-90000],
                    [ 10, 3, 30, 15, 29, 12,  190, 55,  180, 20, 20, 4000,  140,  135,  130,  130,  200,  135,  135, 90000]]),
          
          np.array([[-15,  0,-35,-15,-34,-25,-1000,-40,-1000,-30,-30,-1000,-9500,-9500,-9500,-9500,-9500,-9500,-9500,-30000],
                    [ 10, 10, 30, 15, 29, 12,  195, 50, 180,  20, 20, 4000,  140,  135,  130,  130,  200,  135,  135, 40000]])]
#numsall = np.zeros((2,len(coeffs[0][0])))

def check_gobang(l: int, c: int, winn: int):
    '''
    check if a player wins by taking a move at (l,c)
    '''
    # Check horizontal
    count = 0
    i = 0
    while i < MapL-1 and count < WinN-1:
        if board[l][i] and board[l][i] == board[l][i+1]: count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # Check vertical
    count = 0
    i = 0
    while i < MapL-1 and count < WinN-1:
        if board[i][c] and board[i][c] == board[i+1][c]: count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # Check diagonal
    count = 0
    i = 0
    l_ = l - min(l,c); c_ = c - min(l,c)
    while i+l_ < MapL-1 and i+c_ < MapL-1 and count < WinN-1:
        if board[i+l_][i+c_] and board[i+l_+1][i+c_+1] == board[i+l_][i+c_]: count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    
    # Check anti-diagonal
    count = 0
    i = 0
    while c > 0 and l < MapL-1:
        l += 1; c -= 1
    while l-i > 0 and i+c < MapL and count < WinN-1:
        if board[-i+l][i+c] and board[-i+l-1][i+c+1] == board[-i+l][i+c]: count += 1
        else: count = 0
        i += 1
    if count == WinN-1: return 1
    return 0


def auto(player, coeff=0):
    '''
    calculate computer's move.
    '''
    max_score = -np.inf
    ymax = 1; xmax = 1
    # Calculate the scores at each point
    for y in range(MapL):
        for x in range(MapL):
            if not board[y][x]:
                cd = abs(y-MapL/2+0.5) + abs(x-MapL/2+0.5)
                if (not step and cd>3) or (step and not np.any(board[max(y-2, 0) : min(y+3, MapL),
                                                                     max(x-2, 0) : min(x+3, MapL)])):
                    score = -np.inf
                    #print("     ",end='')
                else:
                    board[y][x] = player
                    scores = score_calc(coeffs[coeff], player)
                    score = scores[0] - cd + np.random.randint(-6, 5)    # my score in this move
                    score_opp = scores[1]    # the opponent's score in this move
                    board[y][x] = 3 - player
                    score2 = score_calc(coeffs[coeff], player)[0]       # my score if the opponent take this move
                    # Treatment of 33, 34 and 44
                    if coeffs[coeff][0][12]*3 < score_opp < coeffs[coeff][0][6]*0.5 + coeffs[coeff][0][12]:
                        score -= coeffs[coeff][0][6]
                    if 1.5 < score2 / coeffs[coeff][0][6] < 2.5:
                        score -= coeffs[coeff][0][6] * 0.25
                    elif 1.9 < score2 / coeffs[coeff][0][12] < 2.1 or 0.5 < (score2-coeffs[coeff][0][12]) / coeffs[coeff][0][6] < 1.5:
                        score -= coeffs[coeff][0][6] * 0.5
                    elif 0.5 < score2/coeffs[coeff][0][19] < 3.5:
                        score -= coeffs[coeff][0][12]
                    #print('%5d' % score,end='')
                    if max_score < score:
                        max_score = score; ymax = y+1; xmax = x+1
                    board[y][x] = 0
            else: pass
                #print('  ['+'%s'%chr(21*board[y][x]+45)+']', end='')
        #print("")
    #print("B:", end='')
    #for j in range(len(numsall[0])): print('%2d'%int(numsall[0][j]), end=' ')
    #print("\nW:", end='')
    #for j in range(len(numsall[0])): print('%2d'%int(numsall[1][j]), end=' ')
    #print("")
    return ymax, xmax


def score_calc(coeff,player=2):
    '''calculate total score'''
    nums = np.zeros((2, len(coeffs[0][0])))
    def one_calc(a):
        '''calculate each list'''
        l = len(a)
        a = a.tolist()
        for i in range(l-2):
            if a[i:i+3]==[0,1,0]: nums[0][0]+=1
            elif a[i:i+3]==[2,1,0] or a[i:i+3]==[0,1,2]: nums[0][1]+=1
                
            elif a[i:i+3]==[0,2,0]: nums[1][0]+=1
            elif a[i:i+3]==[1,2,0] or a[i:i+3]==[0,2,1]: nums[1][1]+=1
        for i in range(l-3):
            if a[i:i+4]==[0,1,1,0]: nums[0][2]+=1
            elif a[i:i+4]==[2,1,1,0] or a[i:i+4]==[0,1,1,2]: nums[0][3]+=1
                
            elif a[i:i+4]==[0,2,2,0]: nums[1][2]+=1
            elif a[i:i+4]==[1,2,2,0] or a[i:i+4]==[0,2,2,1]: nums[1][3]+=1
        for i in range(l-4):
            if a[i:i+5]==[0,1,0,1,0]: nums[0][4]+=1
            elif a[i:i+5]==[0,1,0,1,2] or a[i:i+5]==[2,1,0,1,0]: nums[0][5]+=1
            elif a[i:i+5]==[0,1,1,1,0]: nums[0][6]+=1
            elif a[i:i+5]==[0,1,1,1,2] or a[i:i+5]==[2,1,1,1,0]: nums[0][7]+=1
            elif a[i:i+5]==[1,1,1,1,1]: nums[0][-1]+=1
                
            elif a[i:i+5]==[0,2,0,2,0]: nums[1][4]+=1
            elif a[i:i+5]==[0,2,0,2,1] or a[i:i+5]==[1,2,0,2,0]: nums[1][5]+=1
            elif a[i:i+5]==[0,2,2,2,0]: nums[1][6]+=1
            elif a[i:i+5]==[0,2,2,2,1] or a[i:i+5]==[1,2,2,2,0]: nums[1][7]+=1
            elif a[i:i+5]==[2,2,2,2,2]: nums[1][-1]+=1
            
        if l>=6:
            for i in range(l-5):
                if a[i:i+6]==[0,1,0,1,1,0] or a[i:i+6]==[0,1,1,0,1,0]: nums[0][8]+=1
                elif a[i:i+6]==[2,1,0,1,1,0] or a[i:i+6]==[0,1,1,0,1,2]: nums[0][9]+=1
                elif a[i:i+6]==[2,1,1,0,1,0] or a[i:i+6]==[0,1,0,1,1,2]: nums[0][10]+=1
                elif a[i:i+6]==[0,1,1,1,1,0]: nums[0][11]+=1
                elif a[i:i+6]==[2,1,1,1,1,0] or a[i:i+6]==[0,1,1,1,1,2]: nums[0][12]+=1
                elif a[i:i+6]==[1,1,1,0,1,1] or a[i:i+6]==[1,1,0,1,1,1]: nums[0][13]+=1
                    
                elif a[i:i+6]==[0,2,0,2,2,0] or a[i:i+6]==[0,2,2,0,2,0]: nums[1][8]+=1
                elif a[i:i+6]==[1,2,0,2,2,0] or a[i:i+6]==[0,2,2,0,2,1]: nums[1][9]+=1
                elif a[i:i+6]==[0,2,2,0,2,1] or a[i:i+6]==[0,2,0,2,2,1]: nums[1][10]+=1
                elif a[i:i+6]==[0,2,2,2,2,0]: nums[1][11]+=1
                elif a[i:i+6]==[1,2,2,2,2,0] or a[i:i+6]==[0,2,2,2,2,1]: nums[1][12]+=1
                elif a[i:i+6]==[2,2,2,0,2,2] or a[i:i+6]==[2,2,0,2,2,2]: nums[1][13]+=1
                
        if l>=7:
            for i in range(l-6):
                if a[i:i+7]==[0,1,1,1,0,1,0] or a[i:i+7]==[0,1,0,1,1,1,0]: nums[0][16]+=1
                elif a[i:i+7]==[2,1,1,0,1,1,2] or a[i:i+7]==[2,1,0,1,1,1,2] or a[i:i+7]==[2,1,1,1,0,1,2]: nums[0][13]+=1
                elif a[i:i+7]==[2,1,1,0,1,1,0] or a[i:i+7]==[0,1,1,0,1,1,2]: nums[0][14]+=1
                elif a[i:i+7]==[0,1,1,0,1,1,0] or a[i:i+7]==[0,1,1,1,0,1,2] or a[i:i+7]==[2,1,0,1,1,1,0]: nums[0][15]+=1
                elif a[i:i+7]==[0,1,0,1,1,1,2] or a[i:i+7]==[2,1,1,1,0,1,0]: nums[0][17]+=1
                
                elif a[i:i+7]==[0,2,2,2,0,2,0] or a[i:i+7]==[0,2,0,2,2,2,0]: nums[1][16]+=1
                elif a[i:i+7]==[1,2,2,0,2,2,1] or a[i:i+7]==[1,2,0,2,2,2,1] or a[i:i+7]==[1,2,2,2,0,2,1]: nums[1][13]+=1
                elif a[i:i+7]==[1,2,2,0,2,2,0] or a[i:i+7]==[0,2,2,0,2,2,1]: nums[1][14]+=1
                elif a[i:i+7]==[0,2,2,0,2,2,0] or a[i:i+7]==[0,2,2,2,0,2,1] or a[i:i+7]==[1,2,0,2,2,2,0]: nums[1][15]+=1
                elif a[i:i+7]==[0,2,0,2,2,2,1] or a[i:i+7]==[1,2,2,2,0,2,0]: nums[1][17]+=1
        
    for i in range(MapL):
        # Calculate row and column
        one_calc(board[i])
        one_calc(board[:,i])
    for i in range(-MapL+5,MapL-4):
        # Calculate the main and sub diagonals
        one_calc(np.diag(board,i))
        one_calc(np.diag(np.flip(board,axis=0),i))
        
    nums[:,0] -= nums[:,4]*2 + nums[:,8] + nums[:,10] + nums[:,16] + nums[:,17]
    nums[:,1] -= nums[:,5] + nums[:,9]
    nums[:,2] -= nums[:,8] + nums[:,9] + nums[:,14] + nums[:,15]
    nums[:,3] -= nums[:,10] + nums[:,14]
    nums[:,6] -= nums[:,15] + nums[:,16]
    nums[:,7] -= nums[:,17]
    
    #global numsall
    #numsall = nums
    if player == 2:
        return np.sum(nums*coeff), np.sum(nums*np.flip(coeff, axis=0))
    else:
        return np.sum(nums*np.flip(coeff, axis=0)), np.sum(nums*coeff)


def action(event):
    '''
    event handler & modes
    '''
    if not end_flag:
        try:
            if mode == 0:
                move(round(event.ydata), round(event.xdata))
            elif mode == 1:
                if not step % 2: y,x = auto(1,1); move(y,x) # auto(1-B 2-W, 0-Old 1-New)
                else: move(round(event.ydata), round(event.xdata))
            elif mode == 2:
                if not step % 2: move(round(event.ydata), round(event.xdata))
                else: y,x = auto(2); move(y,x)
            elif mode == 3:
                if not step % 2: y,x = auto(1); move(y,x)
                else: y,x = auto(2,1); move(y,x)
        except: pass


def move(i, j):
    '''
    take a move
    '''
    global step, board, end_flag
    if step == MapL**2: end_flag = 2
    try:
        if not board[i-1][j-1]:
            board[i-1][j-1] = step % 2 + 1
            step += 1
            steps.append([i, j])
            if check_gobang(i-1, j-1, WinN): end_flag = 1
            show_board()
    except: pass


def show_board():
    '''
    show the chessboard
    '''
    global step, board
    colors = ['w', 'k', 'w']
    names  = ['player', 'PC']
    adsize = 0 if mode == 3 else step % 2

    plt.clf()
    fig = plt.figure(num=1)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(adsize, 30, 800+adsize, 800)   # position and size of the window
    fig.canvas.mpl_connect('button_press_event', action)
    plt.xlim(0.5, MapL+0.5)
    plt.ylim(0.5, MapL+0.5)
    for i in range(MapL):
        for j in range(MapL):
            if board[i][j]:
                plt.scatter(j+1, i+1,
                            c=colors[board[i][j]], s=8000/(MapL-1),
                            lw=1, ec='k', zorder=128)
    if step:
        plt.scatter(steps[-1][1], steps[-1][0], s=100, c='r', lw=5, marker='+', zorder=256)
    if MapL == 15:
        plt.scatter([4,4,8,12,12], [4,12,8,4,12], c='k', s=10, zorder=2)
    else:
        plt.scatter([4,4,MapL-3,MapL-3], [4,MapL-3,4,MapL-3], c='k', s=10, zorder=2)
    
    plt.plot([1, 1, MapL, MapL, 1],[1, MapL, MapL, 1, 1], c='k', lw=1)
    plt.fill([1, MapL, MapL, 1], [1, 1, MapL, MapL], c='tan', alpha=0.5, zorder=0)
    plt.fill([-MapL, 2*MapL, 2*MapL, -MapL], [-MapL, -MapL, 2*MapL, 2*MapL], c='tan', alpha=0.4, zorder=1)

    plt.grid(True, ls='--',c='k',zorder=1)
    plt.text(MapL/2, MapL+1.5,
             f"Step:{str(step)}  Black:{names[mode & 1]}  {str(result[0])}:{str(result[1])}  White:{names[(mode & 2)//2]}",
             fontsize=15, ha="center")
    ax = plt.gca()
    ax.set_xticks(range(1, MapL+1))
    ax.set_yticks(range(1, MapL+1))
    for edge in ['left', 'right', 'top', 'bottom']: ax.spines[edge].set_visible(False)
    if end_flag:
        if end_flag == 2:
            string = "Draw!"
        else:
            string = "Black wins" if step%2 else "White wins"
        plt.text(MapL/2+0.5, MapL+0.5, string, fontsize=20, c='r', va="center", ha="center")
        plt.text(MapL/2+0.5, MapL-0.5, 'close the panel to start a new game!', fontsize=12, c='r', va="center", ha="center")

    if mode & (step % 2 + 1):
        if not step: plt.pause(0.01)
        fig.canvas.draw_idle()
        fig.canvas.start_event_loop(0.1)
        if not end_flag: plt.clf()
        action(1)
    else:
        plt.show()


def init():
    '''
    Initialization the interface.
    '''
    def choice(event):
        global mode
        mode = 4 - round(event.ydata)
        if mode in [0,1,2,3] and 2.3 < event.xdata < 7.7: plt.close(0)

    fig = plt.figure(num=0)
    plt.rcParams['font.family'] = 'monospace'
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(100, 100, 600, 600)
    fig.canvas.mpl_connect('button_press_event', choice)
    
    plt.xlim(0,10)
    plt.ylim(0,10)
    plt.xticks([])
    plt.yticks([])
    plt.text(5, 8, "  Gobang  ", fontsize=25, c="w", bbox=(dict(fc="k", alpha=0.5)), va="center", ha="center")
    plt.text(5, 5.7, "Click the chessboard to play.\n Close the chessboard to refresh\n or start a new game.", fontsize=13, va="center", ha="center")
    plt.text(5, 4, '● player vs ○ player ', fontsize=15, bbox=dict(fc=(1, 0.85, 0.7)), va="center", ha="center")
    plt.text(5, 2, '● player vs ○ PC     ', fontsize=15, bbox=dict(fc=(1, 0.85, 0.7)), va="center", ha="center")
    plt.text(5, 3, '● PC     vs ○ player ', fontsize=15, bbox=dict(fc=(1, 0.85, 0.7)), va="center", ha="center")
    plt.text(5, 1, '● PC     vs ○ PC     ', fontsize=15, bbox=dict(fc=(1, 0.85, 0.7)), va="center", ha="center")
    img = plt.imread("img.jpg")
    plt.imshow(img, extent=[0, 10, 5, 10])
    plt.show()
    if mode == 4: exit()

if __name__ == "__main__":
    result = [0, 0]
    init()
    while 1:
        show_board()
        if end_flag:
            if end_flag == 2: pass
            elif step % 2: result[0] += 1
            else: result[1] += 1
            end_flag = 0
            step = 0
            steps.clear()
            board[board != 0] = 0
            print(f"\n----- SCORE -----\nBlack {result[0]} - {result[1]} White\n" + "-"*17)
