import skvideo.io
import skvideo.datasets
import numpy as np

def main(param):
    videodata = skvideo.io.vread(skvideo.datasets.bigbuckbunny())
    print(videodata.shape)

    outputdata = np.random.random(size=(5, 480, 680, 3)) * 255
    outputdata = outputdata.astype(np.uint8)

    writer = skvideo.io.FFmpegWriter("/proxy/exec/video/outputvideo.mp4")
    #writer = skvideo.io.FFmpegWriter("outputvideo.mp4")

    for i in range(5):
        writer.writeFrame(outputdata[i, :, :, :])
    writer.close()

#main({})
