from scipy import stats
import numpy as np

import time
import cv2
import os

from grab_key import arrow_left, arrow_right
from grab_key import get_keys
from grab_screen import get_screen
from stitch import affineStitch

if __name__ == '__main__':

    imageLeft = None
    imageRight = None

    # debug
    # extension = 'png'
    # dataFolder = 'data'
    # imageFileLeft = '{}/stitched_001.{}'.format(dataFolder, extension)
    # imageFileRight = '{}/image_002.{}'.format(dataFolder, extension)

    # imageLeft = cv2.imread(imageFileLeft)
    # imageRight = cv2.imread(imageFileRight)

    print('Starting in 3 seconds, get ready!')
    for i in range(3):
        print('{}'.format(3-i), end='\r')
        time.sleep(1)

    dataFolder = os.path.join(os.getcwd(), './data')
    # dataFolder = os.path.join(os.getcwd(), './debug')
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)

    print('Press Q to quit!')
    
    current_position = 0
    movement_vector = 0
    counter = 0

    while True:
        keys = get_keys()
        if arrow_left in keys:
            movement_vector = -1
            current_position += -1
        elif arrow_right in keys:
            movement_vector = 1
            current_position += 1
        else: 
            movement_vector = 0
        # print('Position: {:3d} | Movement: {:3d} '.format(current_position, movement_vector))

        if imageLeft is None:
            imageLeft = get_screen()
            cv2.imwrite('{}/image_{:03d}.png'.format(dataFolder, 0), imageLeft)
            time.sleep(0.5)
            continue

        imageRight = get_screen()
        stitchedImage, imageCorrespondence = affineStitch(imageLeft, imageRight, movement_vector)

        if stitchedImage is not None:
            # cv2.imwrite('{}/image_{:03d}.png'.format(dataFolder, counter+1), imageRight)
            # cv2.imwrite('{}/stitched_{:03d}.png'.format(dataFolder, counter+1), stitchedImage)
            # print('stitchedImage saved')

            cv2.imwrite('{}/image_{:03d}_left.png'.format(dataFolder, counter+1), imageLeft)
            cv2.imwrite('{}/image_{:03d}_right.png'.format(dataFolder, counter+1), imageRight)
            cv2.imwrite('{}/stitched_{:03d}.png'.format(dataFolder, counter+1), stitchedImage)
            cv2.imwrite('{}/corres_{:03d}.jpg'.format(dataFolder, counter+1), imageCorrespondence)

            imageLeft = stitchedImage
            counter += 1
            # if counter is 5: break
        
        # break

        time.sleep(0.05)
        if 'Q' in keys:
            break