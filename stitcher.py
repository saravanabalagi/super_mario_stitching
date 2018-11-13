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
    
    ptsA = np.float32([kpLeft[i.queryIdx].pt for i in goodMatches])
    ptsB = np.float32([kpRight[i.trainIdx].pt for i in goodMatches])
    
    if len(ptsA)<3 or len(ptsB)<3: return None
    M = cv2.getAffineTransform(ptsB[:3],ptsA[:3])
    warpedImage = cv2.warpAffine(imageRight,M,(imageLeft.shape[1]+imageRight.shape[1],imageLeft.shape[0]))
    warpedImage[:, 0:imageLeft.shape[1], :] = imageLeft
    
    homographyMatrix = np.eye(3)
    homographyMatrix[0,2] = M[0,2]
    homographyMatrix[1,2] = M[1,2]
    
    w2,h2 = imageRight.shape[:2]
    imageRightTempDim = np.float32([ [0,0], [0,w2], [h2, w2], [h2,0] ]).reshape(-1,1,2)
    imageRightDim = cv2.perspectiveTransform(imageRightTempDim, homographyMatrix)
    rightEdge = int(np.min(imageRightDim[2:].T[0]))
    return warpedImage[:, :rightEdge, :]

if __name__ == '__main__':

	imageLeft = None
	imageRight = None

	print('Starting in 3 seconds, get ready!')
	for i in range(3):
		print('{}'.format(3-i), end='\r')
		time.sleep(1)

	print('Press Q to quit!')
	while True:
		keys = get_keys()

		if imageLeft is None:
			imageLeft = get_screen()
			time.sleep(0.5)
			continue

		imageRight = get_screen()
		stitchedImage = affineStitch(imageLeft, imageRight)

		if stitchedImage is not None:
			cv2.imwrite('imageLeft.png', imageLeft)
			cv2.imwrite('imageRight.png', imageRight)
			cv2.imwrite('stitchedImage.png', stitchedImage)
			print('stitchedImage saved')
			break

		time.sleep(0.5)
		if 'Q' in keys:
			break