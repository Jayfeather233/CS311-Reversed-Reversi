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

    dir = np.asarray([(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)])

    map_score = np.asarray(
[[-64,  1, -10,  -5,  -5, -10,   1,  -64],
[  1,   3,  -1,  -1,  -1,  -1,   3,    1],
[-10,  -1,  -3,  -2,  -2,  -3,  -1,  -10],
[ -5,  -1,  -2,  -1,  -1,  -2,  -1,   -5],
[ -5,  -1,  -2,  -1,  -1,  -2,  -1,   -5],
[-10,  -1,  -3,  -2,  -2,  -3,  -1,  -10],
[  1,   3,  -1,  -1,  -1,  -1,   3,    1],
[-64,   1, -10,  -5,  -5, -10,   1,  -64]])

    #chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        #You are white or black
        self.color = color
        #the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as your decision.
        self.candidate_list = []
        
        sz = self.chessboard_size * self.chessboard_size
        
        self.history = np.zeros(shape=(2,sz+5,sz+5), dtype=tuple)
        
        
        for i in range(2):
            for j in range(sz+3):
                for k in range(sz+3):
                    self.history[i][j][k] = tuple((int(k/self.chessboard_size), k%self.chessboard_size))

    def in_range(self, pos):
        return 0<=pos[0] and pos[0]<self.chessboard_size and 0<=pos[1] and pos[1]<self.chessboard_size

    def check_dir(self, chessboard, pos, di, color):
        # now_pos = pos + di
        now_pos = tuple(np.add(pos, di))
        flg = False
        # print('Before' + str(pos) + str(di))
        while self.in_range(now_pos):
            if chessboard[now_pos] == color:
                return flg
            elif chessboard[now_pos] == -color:
                flg = True
            else:
                return False
            now_pos = tuple(np.add(now_pos, di))
            # print(str(now_pos))
        return False
    

    def do_move_dir(self, chessboard, pos, di, color):
        # now_pos = pos + di
        now_pos = tuple(np.add(pos, di))
        # print('Before' + str(pos) + str(di))
        while self.in_range(now_pos) and chessboard[now_pos] != color:
            chessboard[now_pos] = color
            now_pos = tuple(np.add(now_pos, di))
            # print(str(now_pos))
    

    def check(self, chessboard, pos, color):
        return any(self.check_dir(chessboard, pos, di, color) for di in self.dir)
    
    def evaluate(self, chessboard, color, type = False):
        score = 0
        if not type:
            # for i in range(8):
            #     for j in range(8):
            #         score += chessboard[i][j] * self.map_score[i][j]
            score = np.sum(chessboard * self.map_score)
            # score += (len(self.get_candidate(chessboard, color)) - len(self.get_candidate(chessboard, -color)))*7
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
        
        def max_value(chessboard, id, step, alpha, beta, is_skiped, evaluate_type):
            # print(chessboard)
            if step == 0:
                return self.evaluate(chessboard, player, evaluate_type), None
            actions = self.get_candidate(chessboard, player)
            if len(actions) == 0:
                if is_skiped:
                    return self.evaluate(chessboard, player, True) * 1000, None # end state
                else:
                    return min_value(chessboard, id, step, alpha, beta, True, evaluate_type)[0], None
            v, move = -math.inf, None
            for i in range(64):
                a = self.history[0][id][i]
                # print(a)
                if not a in actions:
                    continue
                v2, _ = min_value(self.do_move(chessboard, a, player), id, step - 1, alpha, beta, False, evaluate_type)
                if v < v2:
                    v, move = v2, a
                
                if v>= beta:
                    self.float_move(0,id,i)
                    break
                if alpha < v:
                    self.advantage_move(0,id,i)
                    alpha = v
                    
            return v, move
                
                
        def min_value(chessboard, id, step, alpha, beta, is_skiped, evaluate_type):
            if step == 0:
                return self.evaluate(chessboard, player, evaluate_type), None
            actions = self.get_candidate(chessboard, -player)
            if len(actions) == 0:
                if is_skiped:
                    return self.evaluate(chessboard, player, True) * 1000, None # end state
                else:
                    return max_value(chessboard, id + 1, step, alpha, beta, True, evaluate_type)[0], None
            v, move = math.inf, None
            for i in range(64):
                a = self.history[1][id][i]
                if not a in actions:
                    continue
                v2, _ = max_value(self.do_move(chessboard, a, -player), id + 1, step - 1, alpha, beta, False, evaluate_type)
                if v > v2:
                    v, move = v2, a
                    
                if v <= alpha:
                    self.float_move(1, id, i)
                    break
                if beta > v:
                    self.advantage_move(1, id, i)
                    beta = v
                    
            return v, move
        
        l = int(len(np.where(chessboard == player)[0]))
        # print(l)
        return max_value(chessboard, l, step, -math.inf, math.inf, False, False)
    
    def get_candidate(self, chessboard, color):
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        mlist = list()
        for u in idx:
            if self.check(chessboard, u, color):
                mlist.append(u)
        return mlist

    # The input is the current chessboard. Chessboard is a numpy array.
    def go(self, chessboard):
        # Clear candidate_list, must do this step
        self.candidate_list.clear()
        #==================================================================
        #Write your algorithm here
        #Here is the simplest sample:Random decision

        self.candidate_list = self.get_candidate(chessboard, self.color)

        if len(np.where(chessboard == COLOR_NONE)[0]) < 10:
            move = self.min_max(chessboard, 10)[1]
        else:
            # move = self.ID_minmax(chessboard, self.time_out)
            move = self.min_max(chessboard, 6)[1]
        if move != None:
            self.candidate_list.append(move)
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
