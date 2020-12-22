import time
import os

def main(params):
    start = time.time()

    os.system("python3 /proxy/exec/map_reduce/word_count.py /proxy/exec/map_reduce/data.txt")
    #os.system("python3 word_count.py data.txt")
    print("latency:", time.time() - start)

