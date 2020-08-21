import numpy as np
from time import time

def main(param):
    n = param["param"]
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    print('latency :',latency)
    return {"latency":latency}

main({'param':2000})
