import subprocess
import time

tmp = '/action/disk/tmp/'

"""
dd - convert and copy a file
man : http://man7.org/linux/man-pages/man1/dd.1.html
Options
 - bs=BYTES
    read and write up to BYTES bytes at a time (default: 512);
    overrides ibs and obs
 - if=FILE
    read from FILE instead of stdin
 - of=FILE
    write to FILE instead of stdout
 - count=N
    copy only N input blocks
"""
def main(param):
    #bs = 'bs='+param.get('bs')
    #count = 'count='+param.get('count')
    bs = 'bs='+str(param["bs"])
    count = 'count='+str(param["count"])
    out_fd = open(tmp + 'io_write_logs', 'w')
    start = time.time()
    dd = subprocess.Popen(['dd', 'if=/dev/zero', 'of=/dev/null', bs, count],stderr=out_fd)
    dd.communicate()
    subprocess.check_output(['ls', '-alh', tmp])
    latency = time.time()-start
    #with open(tmp + 'io_write_logs') as logs:
        #result = str(logs.readlines()[2]).replace('\n', '')
        #result = logs.readlines()
    print('latency :',latency)
    return {"latency":latency}

#main({"bs":2048,"count":50000})

