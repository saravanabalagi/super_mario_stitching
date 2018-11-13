import win32gui, win32ui, win32con, win32api
import numpy as np
import cv2
import os
import threading

# Constants
SCREEN_X_START = 2
SCREEN_Y_START = 70
SCREEN_X_END = 520
SCREEN_Y_END = 520

COUNTER = 1
PATH = os.path.join(os.getcwd(), './screenshots')

def get_screen(x_start=SCREEN_X_START, x_end=SCREEN_X_END, y_start=SCREEN_Y_START, y_end=SCREEN_Y_END):
    hwin = win32gui.GetDesktopWindow()

    width = x_end - x_start
    height = y_end - y_start
    left = x_start
    top = y_start

    if width==0 or height==0:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img

def get_scaled_grayscale(img):
	img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	img = cv2.resize(img, (100, 75))
	return img

def save_image(img):
	global COUNTER
	threading.Thread(target=write_image, args=(img, COUNTER, )).start()
	COUNTER += 1

def write_image(img, number):
	global PATH
	if not os.path.exists(PATH):
		os.makedirs(PATH)
	screen_bg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	cv2.imwrite(os.path.join(PATH, 'screen_' + '{0:03d}'.format(number) + '.jpg'), img)

if __name__ == '__main__':
    image = get_screen()
    print(image.shape)
    # print(image[:,:,3])
    save_image(image)