from PIL import Image,ImageFilter
import os
import time

file_name = "test_image.png"
image = Image.open("/proxy/exec/image/"+file_name,"r")
save_path = "/proxy/exec/image/result/"

#image = Image.open(file_name,"r")
#save_path = "result/"


def flip(image, file_name):
    path_list = []
    path = save_path + "flip-left-right/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(path + file_name)
    path_list.append(path)

    path = save_path + "flip-top-bottom/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path + file_name)
    path_list.append(path)
    return path_list

def rotate(image, file_name):
    path_list = []
    path = save_path + "rotate-90/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.transpose(Image.ROTATE_90)
    img.save(path + file_name)
    path_list.append(path)

    path = save_path + "rotate-180/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.transpose(Image.ROTATE_180)
    img.save(path + file_name)
    path_list.append(path)

    path = save_path + "rotate-270/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.transpose(Image.ROTATE_270)
    img.save(path + file_name)
    path_list.append(path)

    return path_list

def i_filter(image, file_name):
    path_list = []
    path = save_path + "blur/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.filter(ImageFilter.BLUR)
    img.save(path + file_name)
    path_list.append(path)

    path = save_path + "contour/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.filter(ImageFilter.CONTOUR)
    img.save(path + file_name)
    path_list.append(path)

    path = save_path + "sharpen/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.filter(ImageFilter.SHARPEN)
    img.save(path + file_name)
    path_list.append(path)

    return path_list

def gray_scale(image, file_name):
    path = save_path + "gray-scale/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    img = image.convert('L')
    img.save(path + file_name)
    return [path]

def resize(image, file_name):
    path = save_path + "resized/"
    #if not os.path.exists(path):
    #    os.makedirs(path)
    image.thumbnail((128, 128))
    image.save(path + file_name)
    return [path]

def image_processing(image,file_name):
    path_list = []
    start = time.time()
    path_list += flip(image, file_name)
    path_list += rotate(image, file_name)
    path_list += i_filter(image, file_name)
    path_list += gray_scale(image, file_name)
    path_list += resize(image, file_name)

    latency = time.time() - start
    return latency, path_list

def main(params):
    latency, path_list = image_processing(image,file_name)
    print(latency)
    print(path_list)

