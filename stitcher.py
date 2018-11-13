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
    	return None
    
    ptsA = np.float32([kpLeft[m.queryIdx].pt for m in goodMatches])
    ptsB = np.float32([kpRight[m.trainIdx].pt for m in goodMatches])
    
    distances = np.array([kpLeft[m.queryIdx].pt[0] - kpRight[m.trainIdx].pt[0] for m in goodMatches])
    losses = np.array([np.sum(abs(distances - d)) for d in distances])
#     print(np.median(distances), np.mean(distances), stats.mode(distances).mode[0])
#     print(np.argmin(losses), distances[np.argmin(losses)])

    requiredWidth = int(np.round(distances[np.argmin(losses)]))
    warpedImage = np.zeros(np.array(imageLeft.shape) + (0, requiredWidth, 0), dtype='uint8')
    print(warpedImage.shape, imageRight.shape)
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

	print('Press Q to quit!')
	counter = 0
	while True:
		keys = get_keys()

		if imageLeft is None:
			imageLeft = get_screen()[:,:,::-1]
			time.sleep(0.5)
			continue

		imageRight = get_screen()[:,:,::-1]
		stitchedImage = affineStitch(imageLeft, imageRight)

		if stitchedImage is not None:
			cv2.imwrite('imageLeft.png', imageLeft[:,:,::-1])
			cv2.imwrite('imageRight.png', imageRight[:,:,::-1])
			cv2.imwrite('stitchedImage.png', stitchedImage[:,:,::-1])
			print('stitchedImage saved')

			imageLeft = stitchedImage
			counter += 1
			if counter is 2: break

		time.sleep(0.25)
		if 'Q' in keys:
			break