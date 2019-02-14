import os
from PIL import Image
import numpy as np

front_image_path = '/media/stian/Evan Dutch/Bifurcation/12805/05-02-2019/front/2853/2853_'
back_image_path = '/media/stian/Evan Dutch/Bifurcation/12805/05-02-2019/back/2851/2851_'

front_img_px = 1150
back_img_px = 230
image_count = 1000

for i in range(image_count):
    print('Stitching image ' + str(i+1) + '/' + str(image_count), end='\r')
    num = ('0000'+ str(i+1))[-4:]
    front_path = front_image_path + num + '.bmp'
    back_path = back_image_path + num + '.bmp'

    front_img = Image.open(front_path)
    front_img = np.array(front_img)[0:800, front_img_px-740:1280]
    back_img = Image.open(back_path)
    back_img = np.array(back_img)[0:800, 0:back_img_px+640]
    #back_img = np.flip(back_img,0)

    stitched_img = np.concatenate((back_img, front_img), axis=1)
    result = Image.fromarray((stitched_img).astype(np.uint8))
    result.save('/media/stian/Evan Dutch/Bifurcation/12805/05-02-2019/stitched/285/285_' + num + '.bmp')

print()

# back_img = np.flip(back_img, 0)
# result = Image.fromarray((back_img).astype(np.uint8))
# result.show()