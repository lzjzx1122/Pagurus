import time
import os


start = time.time()

os.system("python3 /action/map_reduce/word_count.py /action/map_reduce/data.txt")
#os.system("python3 word_count.py data.txt")
print("latency:", time.time() - start)
