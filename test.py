import main
import numpy as np

def print_board(chessboard):
    print(end='  ')
    for i in range(8):
        print(i, end=' ')
    print('\n', end='')
    for i in range(8):
        for j in range(8):
            if j ==0:
                print(i, end=' ')
            if chessboard[i][j] == 1:
                print("O ", end='')
            elif chessboard[i][j] == -1:
                print("X ", end='')
            else:
                print("  ", end='')
        print('\n', end='')

def print_evaluate(eva):
    print()
    print(end='  ')
    for i in range(8):
        print(i, end=' ')
    print('\n', end='')
    for i in range(8):
        for j in range(8):
            print(eva[i][j], end=' ')
        print('\n', end='')

if __name__ == "__main__":
    agent1 = main.AI(8,1,5)
    agent2 = main.AI(8,-1,5)
    cb = np.zeros(shape=(8,8))
    cb[(3,3)]=1
    cb[(4,4)]=1
    cb[(3,4)]=-1
    cb[(4,3)]=-1
    while True:
        print_board(cb)
        # x=int(input())
        # y=int(input())
        # cb = agent.do_move(cb, (x,y), -1)
        agent1.go(cb)
        # print_evaluate(agent.map_evaluate)
        # print(agent.candidate_list)
        cb = agent1.do_move(cb, agent1.candidate_list[len(agent1.candidate_list)-1], 1)
        print_board(cb)
        agent2.go(cb)
        # print_evaluate(agent.map_evaluate)
        # print(agent.candidate_list)
        cb = agent1.do_move(cb, agent2.candidate_list[len(agent2.candidate_list)-1], -1)