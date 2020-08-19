import time
import os

def main(params):
    start = time.time()

    os.system("python3 /proxy/exec/word_count.py /proxy/exec/data.txt")
    #os.system("python3 word_count.py data.txt")
    print("latency:", time.time() - start)

