import time
import markdown

def main(param):
    start = time.time()

    runtime = param['runtime']
    time.sleep(runtime)

    latency = time.time() - start
    return {"latency": latency}

