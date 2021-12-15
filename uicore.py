import win32gui, win32con, win32com.client, win32process, win32api
import time

def is_fullscreen(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    return style | win32con.WS_SYSMENU != style

def is_borderless(hwnd,current_style):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    return style == current_style

def is_minecraft():
    active_hwnd = win32gui.GetForegroundWindow()
    class_name = win32gui.GetClassName(active_hwnd)
    return class_name == "LWJGL"

def is_mouse_down():
    return win32api.GetKeyState(0x01) < 0 or win32api.GetKeyState(0x02) < 0

def get_minecraft_hwnd():
    return win32gui.FindWindow("LWJGL", None)

def get_active_hwnd():
    return win32gui.GetForegroundWindow()

def get_mouse_pos():
    return win32api.GetCursorPos()

def free_cursor():
    win32api.ClipCursor((0,0,0,0))

def set_active_hwnd(hwnd):
    return win32gui.SetForegroundWindow(hwnd)

def set_borderless(hwnd=None,state=True):
    style_BL =  win32con.WS_DLGFRAME | win32con.WS_CLIPSIBLINGS | win32con.WS_CLIPCHILDREN | win32con.WS_VISIBLE
    style_Normal =  win32con.WS_DLGFRAME | win32con.WS_CLIPSIBLINGS | win32con.WS_CLIPCHILDREN | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_SYSMENU | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX
    if not hwnd: hwnd = get_minecraft_hwnd()
    
    if state:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style_BL)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    else:
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style_Normal)
        win32gui.MoveWindow(hwnd, 100, 100, 1000, 600, False)
        time.sleep(0.05)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    
    free_cursor()

def set_clickthrough(hwnd,state):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if state: style = style | win32con.WS_EX_TRANSPARENT
    else:     style = style & ~win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

def remove_exit_button(hwnd):
    try:
        hMenu = win32gui.GetSystemMenu(hwnd, 0)
        if hMenu:
            win32gui.DeleteMenu(hMenu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)
    except Exception:
        pass

if __name__ == "__main__":
    while True:
        time.sleep(1)
        
        mc_hwnd = get_minecraft_hwnd()
        sty = win32gui.GetWindowLong(mc_hwnd, win32con.GWL_STYLE)
        styex = win32gui.GetWindowLong(mc_hwnd, win32con.GWL_EXSTYLE)
        focus = win32gui.GetForegroundWindow()
        
        print(mc_hwnd,sty,styex,focus)
        
        #print("logger>",mc_hwnd,win32api.GetCursorPos())
        set_hwnd = None
        if is_fullscreen(mc_hwnd) and mc_hwnd!=set_hwnd:
            set_borderless(mc_hwnd)
            print("fullscreen")
            set_hwnd = mc_hwnd
