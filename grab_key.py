import win32api, win32con

keyList = ["\b"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'/\\":
    keyList.append(char)

arrow_up = win32con.VK_UP
arrow_down = win32con.VK_DOWN
arrow_left = win32con.VK_LEFT
arrow_right = win32con.VK_RIGHT

keyCodeList = [arrow_up, arrow_down, arrow_left, arrow_right]


def get_keys():
    keys = []
    for key in keyList:
        if win32api.GetAsyncKeyState(ord(key)):
            keys.append(key)
    for keycode in keyCodeList:
        if win32api.GetAsyncKeyState(keycode):
            keys.append(keycode)
    return keys
