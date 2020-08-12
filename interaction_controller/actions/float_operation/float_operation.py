import math
import time

def main(param):
    start_time = time.time()
    param = param['param']
    for i in range(0, param):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    print('latency:',time.time()-start_time)
#main({"param":1000000})

