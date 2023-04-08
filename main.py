import numba
import numpy as np
import random
import time 
import math
from numba import jit

COLOR_BLACK=-1
COLOR_WHITE=1
COLOR_NONE=0

random.seed(0)

#don't change the class name
class AI(object):

    dir = np.asarray([(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)], dtype=int)

    map_score = np.asarray(
[[-40,   7, -10,  -5,  -5, -10,   7, -40],
[   7,   5,  -4,  -2,  -2,  -4,   5,   7],
[ -10,  -4,  -4,  -3,  -3,  -4,  -4, -10],
[  -5,  -2,  -3,  -2,  -2,  -3,  -2,  -5],
[  -5,  -2,  -3,  -2,  -2,  -3,  -2,  -5],
[ -10,  -4,  -4,  -3,  -3,  -4,  -4, -10],
[   7,   5,  -4,  -2,  -2,  -4,   5,   7],
[ -40,   7, -10,  -5,  -5, -10,   7, -40]], dtype=float)
    
    map_evaluate = np.zeros(shape=(8,8), dtype=float)

    #chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        #You are white or black
        self.color = color
        #the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out * 1000000000 - 200000000
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as your decision.
        self.candidate_list = []
        
        sz = self.chessboard_size * self.chessboard_size
        
        self.history = np.zeros(shape=(2,sz+5,sz+5), dtype=tuple)
        
        
        for i in range(2):
            for j in range(sz+3):
                for k in range(sz+3):
                    self.history[i][j][k] = tuple((int(k/self.chessboard_size), k%self.chessboard_size))

    def in_range(self, pos):
        return 0<=pos[0]<self.chessboard_size and 0<=pos[1]<self.chessboard_size

    def check_dir(self, chessboard, pos, di, color):
        # now_pos = pos + di
        now_pos = (pos[0]+di[0],pos[1]+di[1])
        flg = False
        # print('Before' + str(pos) + str(di))
        while self.in_range(now_pos):
            if chessboard[now_pos] == color:
                return flg
            elif chessboard[now_pos] == -color:
                flg = True
            else:
                return False
            now_pos = (now_pos[0]+di[0],now_pos[1]+di[1])
            # print(str(now_pos))
        return False
    

    def do_move_dir(self, chessboard, pos, di, color):
        # now_pos = pos + di
        now_pos = (pos[0]+di[0],pos[1]+di[1])
        # print('Before' + str(pos) + str(di))
        while self.in_range(now_pos) and chessboard[now_pos] != color:
            chessboard[now_pos] = color
            now_pos = (now_pos[0]+di[0],now_pos[1]+di[1])
            # print(str(now_pos))
    

    def check(self, chessboard, pos, color):
        return any(self.check_dir(chessboard, pos, di, color) for di in self.dir)
    
    def evaluate(self, chessboard, color, type = False):
        score = 0
        if not type:
            score = np.sum(chessboard * self.map_score)
        else:
            score = np.sum(chessboard) * -1
        return score * color
        
    def do_move(self, chessboard, pos, color):
        cbd = np.copy(chessboard)
        cbd[pos]=color
        for di in self.dir:
            if self.check_dir(cbd, pos, di, color):
                self.do_move_dir(cbd, pos, di, color)
        return cbd
    
    def float_move(self, player, id, pos):
        tmp = self.history[player][id][pos]
        for i in range(pos, 0, -1):
            self.history[player][id][i] = self.history[player][id][i-1]
        self.history[player][id][0]=tmp
        return
    
    def advantage_move(self, player, id, pos):
        if pos!=0 :
            self.history[player][id][pos-1], self.history[player][id][pos] = self.history[player][id][pos], self.history[player][id][pos-1]
        return
    
    # return (score, pos)
    # score: int
    # pos: tuple(x, y)
    def min_max(self, chessboard, step):
        
        player = self.color
        
        def max_value(chessboard, len_player, len_nplayer, step, alpha, beta, is_skiped, evaluate_type):
            if self.cnt % 1000 == 0:
                if time.time_ns() - self.start_time > self.time_out:
                    # print(self.cnt, time.time_ns(), '\n')
                    return self.evaluate(chessboard, player, evaluate_type), None
            self.cnt += 1
            # print(chessboard)
            if step == 0: # or (time.thread_time_ns() - self.start_time) > self.time_out:
                return self.evaluate(chessboard, player, evaluate_type), None

            v, move = -math.inf, None
            for i in range(64):
                a = self.history[0][len_player][i]
                # print(a)
                if chessboard[a] != COLOR_NONE or not self.check(chessboard, a, player):
                # if not (a in actions):
                    continue
                v2, _ = min_value(self.do_move(chessboard, a, player), len_nplayer, len_player + 1, step - 1, alpha, beta, False, evaluate_type)
                # if step == 6:
                #     self.map_evaluate[a] = v2
                if v < v2:
                    v, move = v2, a
                
                if v>= beta:
                    self.float_move(0,len_player,i)
                    break
                if alpha < v:
                    self.advantage_move(0,len_player,i)
                    alpha = v
            
            if move == None:
                if is_skiped:
                    return self.evaluate(chessboard, player, True) * 10000, None # end state
                else:
                    return min_value(chessboard, len_nplayer, len_player, step, alpha, beta, True, evaluate_type)[0], None
                    
            return v, move
                
                
        def min_value(chessboard, len_player, len_nplayer, step, alpha, beta, is_skiped, evaluate_type):
            if self.cnt % 1000 == 0:
                if time.time_ns() - self.start_time > self.time_out:
                    # print(self.cnt, time.time_ns(), '\n')
                    return self.evaluate(chessboard, player, evaluate_type), None
            self.cnt += 1
            
            if step == 0: # or (time.thread_time_ns() - self.start_time) > self.time_out:
                return self.evaluate(chessboard, player, evaluate_type), None
            
            v, move = math.inf, None
            for i in range(64):
                a = self.history[1][len_player][i]
                if chessboard[a] != COLOR_NONE or not self.check(chessboard, a, -player):
                # if not (a in actions):
                    continue
                v2, _ = max_value(self.do_move(chessboard, a, -player), len_nplayer, len_player + 1, step - 1, alpha, beta, False, evaluate_type)
                if v > v2:
                    v, move = v2, a
                    
                if v <= alpha:
                    self.float_move(1, len_player, i)
                    break
                if beta > v:
                    self.advantage_move(1, len_player, i)
                    beta = v
                    
            if move == None:
                if is_skiped:
                    return self.evaluate(chessboard, player, True) * 10000, None # end state
                else:
                    return max_value(chessboard, len_nplayer, len_player, step, alpha, beta, True, evaluate_type)[0], None
                    
            return v, move
        
        # l = int(len(np.where(chessboard == player)[0]))
        # len_player = int(len(np.where(chessboard == player)[0]))
        # len_nplayer = int(len(np.where(chessboard == -player)[0]))
        len_player = len_nplayer = int((64 - int(len(np.where(chessboard == COLOR_NONE)))) / 2)
        # print(l)
        return max_value(chessboard, len_player, len_nplayer, step, -math.inf, math.inf, False, False)
    
    def get_candidate(self, chessboard, color):
        mlist = list()
        for x1 in range(self.chessboard_size):
            for x2 in range(self.chessboard_size):
                if chessboard[x1][x2]==COLOR_NONE and self.check(chessboard, (x1,x2), color):
                    mlist.append((x1,x2))
        return mlist

    # The input is the current chessboard. Chessboard is a numpy array.
    def go(self, chessboard):
        self.map_evaluate.fill(0)
        # Clear candidate_list, must do this step
        self.candidate_list.clear()
        #==================================================================
        #Write your algorithm here
        #Here is the simplest sample:Random decision

        self.candidate_list = self.get_candidate(chessboard, self.color)
        
        self.start_time = time.time_ns()
        self.cnt = 0
        # print('time:', self.start_time)
        
        l = len(np.where(chessboard == COLOR_NONE)[0])
        low_bound = 10 if l <= 13 else 6
        low_bound = min(low_bound, l)
        
        for k in range(low_bound, l+2):
            move = self.min_max(chessboard, k)[1]
            if time.time_ns() - self.start_time > self.time_out:
                print(k, self.cnt, (time.time_ns() - self.start_time) / 1000000000, '\n')
                break
            if move != None:
                self.candidate_list.append(move)
        
        
        # low_bound = 3
        # k = len(np.where(chessboard == COLOR_NONE)[0])
        # if k < 13:
        #     low_bound = 13
        # else:
        #     low_bound = 7
        # las_move = None
        # move = None
        # move = self.min_max(chessboard, low_bound - 2)[1]
        # las_move = move
        # if las_move != None:
        #     self.candidate_list.append(las_move)
        
        # move = self.min_max(chessboard, low_bound)[1]
        # las_move = move
        # if las_move != None:
        #     self.candidate_list.append(las_move)
        
        
        
        # print('time:', time.thread_time_ns())
        #==============Find new pos========================================
        # Make sure that the position of your decision on the chess board is empty. 
        # If not, the system will return error.
        # Add your decision into candidate_list, Records the chessboard
        # You need to add all the positions which are valid
        # candidate_list example: [(3,3),(4,4)]
        # You need append your decision at the end of the candidate_list, 
        #candidate_list example: [(3,3),(4,4),(4,4)]
        # we will pick the last element of the candidate_list as the position you choose.
        #In above example, we will pick (4,4) as your decision.
        # If there is no valid position, you must return an empty list.
