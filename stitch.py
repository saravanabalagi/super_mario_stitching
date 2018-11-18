import numpy as np
import cv2

def affine_stitch(imageLeft, imageRight):
    orb = cv2.ORB_create()
    kpLeft, desLeft = orb.detectAndCompute(imageLeft, None)
    kpRight, desRight = orb.detectAndCompute(imageRight, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desLeft, desRight)
    
    goodMatches = []
    for m in matches:
    	# if the keypoints are not in the same height reject
        if kpLeft[m.queryIdx].pt[1] != kpRight[m.trainIdx].pt[1]: continue

        # if the keypoints are in the left part of the stitched image, reject
        if kpLeft[m.queryIdx].pt[0] < (imageLeft.shape[1] - imageRight.shape[1]): continue

        if m.distance < 10:
            goodMatches.append(m)

    # print(len(matches), len(goodMatches))

    if len(goodMatches) < 3:
    	print('No Matches')
    	return None, None
    
    ptsA = np.float32([kpLeft[m.queryIdx].pt for m in goodMatches])
    ptsB = np.float32([kpRight[m.trainIdx].pt for m in goodMatches])
    
    distances = np.array([kpLeft[m.queryIdx].pt[0] - kpRight[m.trainIdx].pt[0] for m in goodMatches])
    losses = np.array([np.sum(abs(distances - d)) for d in distances])
    # print(np.median(distances), np.mean(distances), stats.mode(distances).mode[0])
    # print(np.argmin(losses), distances[np.argmin(losses)])

    imageCorrespondence = cv2.drawMatches(imageLeft, kpLeft, imageRight, kpRight, [goodMatches[np.argmin(losses)]], None, flags=2)
    # imshow(imageCorrespondence, newFigure=True)

	# find the translation that minimizes loss
    requiredWidth = int(np.round(distances[np.argmin(losses)]))

    # subtract the extra width so we can print imageRight to the very right
    requiredWidth -= (imageLeft.shape[1] - imageRight.shape[1])
    print('Translation: {:5d} | keypoints: {:5d} {:5d} | Matches: {:5d} / {:5d}'.format(requiredWidth, len(kpLeft), len(kpRight), len(matches), len(goodMatches)))

    # get larger image if there is positive translation
    stitchedImageShape = np.array(imageLeft.shape) + (0, requiredWidth, 0)
    if requiredWidth < 0: 
    	stitchedImageShape = np.array(imageLeft.shape)

    warpedImage = np.zeros(stitchedImageShape, dtype='uint8')
    # print(requiredWidth, imageLeft.shape, imageRight.shape, warpedImage.shape)
    warpedImage[:, -imageRight.shape[1]:, :] = imageRight
    warpedImage[:, 0:imageLeft.shape[1], :] = imageLeft
    return warpedImage, imageCorrespondence