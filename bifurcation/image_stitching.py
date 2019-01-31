import os
from PIL import Image
import numpy as np

front_image_path = '/home/stian/Desktop/Bifurcation/2805/back/2427/2427_'
back_image_path = '/home/stian/Desktop/Bifurcation/2805/front/2427/2427_'

front_img_px = 1176
back_img_px = 295
image_count = 100

for i in range(image_count):
    num = ('0000'+ str(i+1))[-4:]
    front_path = front_image_path + num + '.bmp'
    back_path = back_image_path + num + '.bmp'

    front_img = Image.open(front_path)
    front_img = np.array(front_img)[0:800, 0:back_img_px+640]
    back_img = Image.open(back_path)
    back_img = np.array(back_img)[0:800, front_img_px-740:1280]

    stitched_img = np.concatenate((front_img, back_img), axis=1)
    result = Image.fromarray((stitched_img).astype(np.uint8))
    result.save('/home/stian/Desktop/Bifurcation/2805/stitched/2427_' + num + '.bmp')