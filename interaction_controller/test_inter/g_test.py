import gevent
import time
import _thread

flag = False
def func1():
    print("fun1")
    while True:
        gevent.sleep(0)

def func2():
    print("func2")

def func3():
    print("func3")
    while True:
        func2()
        time.sleep(2)

#_thread.start_new_thread(func1, ())
#_thread.start_new_thread(func3, ())
#_thread.waitall()
#while True:
#    pass
#gevent.spawn(func3)
#gevent.spawn(func1)
#gevent.wait()


gevent.spawn(func1)

gevent.spawn_later(3, func2)
gevent.wait()
