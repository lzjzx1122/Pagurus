import threading
import time

count = 0
def test():
    global count
    n = count
    count += 1
    time.sleep(2)
    for i in range(10):
        print(n)

for i in range(5):
    thread = threading.Thread(target=test)
    thread.start()
    thread.join()
