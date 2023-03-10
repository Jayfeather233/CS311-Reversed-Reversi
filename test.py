import main
import numpy as np

if __name__ == "__main__":
    agent = main.AI(8,1,10)
    cb = np.zeros(shape=(8,8))
    cb[(3,3)]=1
    cb[(4,4)]=1
    cb[(3,4)]=-1
    cb[(4,3)]=-1
    print(cb)
    bu = np.copy(cb)
    cb[0][0]=1
    cb = np.copy(bu)
    print(cb)