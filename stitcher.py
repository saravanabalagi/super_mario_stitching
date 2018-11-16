from scipy import stats
import numpy as np

import time
import cv2
import os

from grab_key import get_keys
from grab_screen import get_screen

def affineStitch(imageLeft, imageRight):
    orb = cv2.ORB_create()
    kpLeft, desLeft = orb.detectAndCompute(imageLeft, None)
    kpRight, desRight = orb.detectAndCompute(imageRight, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desLeft, desRight)
    
    goodMatches = []
    for m in matches:
        if m.distance < 5:
            goodMatches.append(m)

    if len(goodMatches) < 3:
    	print('No Matches')
    	return None
    
    ptsA = np.float32([kpLeft[m.queryIdx].pt for m in goodMatches])
    ptsB = np.float32([kpRight[m.trainIdx].pt for m in goodMatches])
    
    distances = np.array([kpLeft[m.queryIdx].pt[0] - kpRight[m.trainIdx].pt[0] for m in goodMatches])
    losses = np.array([np.sum(abs(distances - d)) for d in distances])
#     print(np.median(distances), np.mean(distances), stats.mode(distances).mode[0])
#     print(np.argmin(losses), distances[np.argmin(losses)])

	# find the translation that minimizes loss
    requiredWidth = int(np.round(distances[np.argmin(losses)]))
    

    # subtract the extra width so we can print imageRight to the very right
    requiredWidth -= (imageLeft.shape[1] - imageRight.shape[1])
    print('Translation', requiredWidth)

    # get larger image if there is positive translation
    stitchedImageShape = np.array(imageLeft.shape) + (0, requiredWidth, 0)
    if requiredWidth < 0: 
    	stitchedImageShape = np.array(imageLeft.shape)

    warpedImage = np.zeros(stitchedImageShape, dtype='uint8')
    # print(imageLeft.shape, imageRight.shape, warpedImage.shape)
    warpedImage[:, -imageRight.shape[1]:, :] = imageRight
    warpedImage[:, 0:imageLeft.shape[1], :] = imageLeft
    return warpedImage

if __name__ == '__main__':

	imageLeft = None
	imageRight = None

	# extension = 'png'
	# imageFileLeft = 'imageLeft.{}'.format(extension)
	# imageFileRight = 'imageRight.{}'.format(extension)

	# imageLeft = cv2.imread(imageFileLeft)[:,:,::-1]
	# imageRight = cv2.imread(imageFileRight)[:,:,::-1]


	print('Starting in 3 seconds, get ready!')
	for i in range(3):
		print('{}'.format(3-i), end='\r')
		time.sleep(1)

	dataFolder = os.path.join(os.getcwd(), './data')
	if not os.path.exists(dataFolder):
		os.makedirs(dataFolder)

	print('Press Q to quit!')
	counter = 0
	while True:
		keys = get_keys()

		if imageLeft is None:
			imageLeft = get_screen()[:,:,::-1]
			cv2.imwrite('{}/image_{:03d}.png'.format(dataFolder, 0), imageLeft[:,:,::-1])
			time.sleep(0.5)
			continue

		imageRight = get_screen()[:,:,::-1]
		stitchedImage = affineStitch(imageLeft, imageRight)

		if stitchedImage is not None:
			cv2.imwrite('{}/image_{:03d}.png'.format(dataFolder, counter+1), imageRight[:,:,::-1])
			cv2.imwrite('{}/stitched_{:03d}.png'.format(dataFolder, counter+1), stitchedImage[:,:,::-1])
			# print('stitchedImage saved')

			imageLeft = stitchedImage
			counter += 1
			# if counter is 5: break

		time.sleep(0.25)
		if 'Q' in keys:
			break