import time
import tox
import moto
import wheel
import freezegun
import sure

def main(param):
    start = time.time()

    runtime = param['runtime']
    time.sleep(runtime)

    latency = time.time() - start
    return {"latency": latency}
