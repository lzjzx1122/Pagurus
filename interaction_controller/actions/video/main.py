import sys
print(sys.path)
from skvideo import io
from skvideo import datasets
import numpy as np

def main(param):
    videodata = io.vread(datasets.bigbuckbunny())
    print(videodata.shape)

    outputdata = np.random.random(size=(5, 480, 680, 3)) * 255
    outputdata = outputdata.astype(np.uint8)

    writer = io.FFmpegWriter("/proxy/exec/outputvideo.mp4")
    #writer = io.FFmpegWriter("outputvideo.mp4")

    for i in range(5):
        writer.writeFrame(outputdata[i, :, :, :])
    writer.close()

main({})
