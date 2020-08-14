#coding:utf-8
import gevent
import gevent.monkey

gevent.monkey.patch_all()

INTERVAL = 10

def schedule(delay, func, *args, **kw_args):
    gevent.spawn_later(0, func, *args, **kw_args)
    gevent.spawn_later(delay, schedule, delay, func, *args, **kw_args)

def test1():
    print ("test1")
    while True:
        yield

def test2():
    print ("test2")

def test3():
    print ("test3")

#schedule(1,test1)
#schedule(2,test2)
gevent.spawn(test1)
schedule(3,test3)

gevent.wait()

