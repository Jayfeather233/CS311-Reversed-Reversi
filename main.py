import numpy as np
import random
import time 

COLOR_BLACK=-1
COLOR_WHITE=1
COLOR_NONE=0

random.seed(0)

#don't change the class name
class AI(object):

    dir = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    #chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        #You are white or black
        self.color = color
        #the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as your decision.
        self.candidate_list = []

    def in_range(self, pos):
        return 0<=pos[0] and pos[0]<self.chessboard_size and 0<=pos[1] and pos[1]<self.chessboard_size

    def check_dir(self, chessboard, pos, di):
        # now_pos = pos + di
        now_pos = tuple(map(sum, zip(pos, di)))
        flg = False
        # print('Before' + str(pos) + str(di))
        while self.in_range(now_pos):
            if chessboard[now_pos] == self.color:
                return flg
            elif chessboard[now_pos] == -self.color:
                flg = True
            else:
                return False
            now_pos = tuple(map(sum, zip(now_pos, di)))
            # print(str(now_pos))
        return False

    def check(self, chessboard, pos):
        return any(self.check_dir(chessboard, pos, di) for di in self.dir)
    
    def evaluate(self, chessboard, type = False):
        score = 0

        for u in chessboard:
            score += u
        return score
    
    def min_max(self, chessboard, step, color):
        if step == 0:
            return (self.evaluate(chessboard), (0,0))
        avaliable_pos = self.get_candidate(chessboard)
        backup = np.copy(chessboard)
        

    
    def get_candidate(self, chessboard):
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        mlist = list()
        for u in idx:
            if self.check(chessboard, u):
                mlist.append(u)
        return mlist

    # The input is the current chessboard. Chessboard is a numpy array.
    def go(self, chessboard):
        # Clear candidate_list, must do this step
        self.candidate_list.clear()
        #==================================================================
        #Write your algorithm here
        #Here is the simplest sample:Random decision

        self.candidate_list = self.get_candidate(chessboard)

        self.candidate_list.append(self.min_max(chessboard, 10, self.color))
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
