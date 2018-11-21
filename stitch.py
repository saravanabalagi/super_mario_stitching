import numpy as np
import cv2


def affineStitch(imageLeft, imageRight, movementVector):
    orb = cv2.ORB_create(nfeatures=5000)
    kpLeft, desLeft = orb.detectAndCompute(imageLeft, None)
    kpRight, desRight = orb.detectAndCompute(imageRight, None)

    if len(kpLeft)==0 or len(kpRight)==0:
        print('No descriptors')
        return None, None

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

    if len(goodMatches) < 1:
        print('No Matches')
        return None, None

    ptsA = np.float32([kpLeft[m.queryIdx].pt for m in goodMatches])
    ptsB = np.float32([kpRight[m.trainIdx].pt for m in goodMatches])

    distances = np.array([kpLeft[m.queryIdx].pt[0] - kpRight[m.trainIdx].pt[0] for m in goodMatches])
    losses = np.array([np.sum(abs(distances - d)) for d in distances])
    # print(np.median(distances), np.mean(distances), stats.mode(distances).mode[0])
    # print(np.argmin(losses), distances[np.argmin(losses)])

    # find the translation that minimizes loss
    translation = int(np.round(distances[np.argmin(losses)]))
    while movementVector > 0 and translation < -40:
        print('entering whileLoop')
        np.delete(losses, np.argmin(losses))
        if len(losses) != 0: translation = int(np.round(distances[np.argmin(losses)]))
        else: return None, None

    # subtract the extra width so we can print imageRight to the very right
    translation -= (imageLeft.shape[1] - imageRight.shape[1])
    print('Translation: {:5d} | keypoints: {:5d} {:5d} | Matches: {:5d} / {:5d}'.format(translation, len(kpLeft),
                                                                                        len(kpRight), len(matches),
                                                                                        len(goodMatches)))


    # draw correspondence
    imageCorrespondence = cv2.drawMatches(imageLeft, kpLeft,
                                          imageRight, kpRight,
                                          [goodMatches[np.argmin(losses)]],
                                          None, flags=2)
    # imshow(imageCorrespondence, newFigure=True)
    # get larger image if there is positive translation
    stitchedImageShape = np.array(imageLeft.shape) + (0, translation, 0)
    if translation < 0:
        stitchedImageShape = np.array(imageLeft.shape)

    warpedImage = np.zeros(stitchedImageShape, dtype='uint8')
    # print(requiredWidth, imageLeft.shape, imageRight.shape, warpedImage.shape)
    warpedImage[:, -imageRight.shape[1]:, :] = imageRight
    warpedImage[:, 0:imageLeft.shape[1], :] = imageLeft
    return warpedImage, imageCorrespondence
