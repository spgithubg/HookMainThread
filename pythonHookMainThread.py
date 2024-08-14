import ctypes
import os
from ctypes import wintypes

import win32api
import win32con
import win32gui
import win32process

# 定义 WNDPROC 类型
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

# 获取 SetWindowLongPtr 和 CallWindowProc 函数
SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW
SetWindowLongPtr.restype = ctypes.c_void_p
CallWindowProc = ctypes.windll.user32.CallWindowProcW
CallWindowProc.restype = ctypes.c_void_p

# 用于存储原始窗口过程的全局变量
original_wnd_proc = None
exit_flag = False


def debug(debug_str):
    win32api.OutputDebugString(f"调试信息: - {str(debug_str)}")


def my_callback(lParam):
    global exit_flag
    debug(f"收到带有 lParam 的自定义消息: {lParam}")
    exit_flag = True


# 钩子过程
def hook_proc(hwnd, msg, wParam, lParam):
    debug(msg)
    if msg == (win32con.WM_USER + 128):
        my_callback(lParam)
        # 在此处处理您的自定义消息

    # 确保所有其他消息都由原始窗口过程处理
    return CallWindowProc(WNDPROC(original_wnd_proc), hwnd, msg, wParam, lParam)


def set_hook(hwnd):
    global original_wnd_proc
    WndProc = WNDPROC(hook_proc)
    original_wnd_proc = SetWindowLongPtr(hwnd, win32con.GWL_WNDPROC, WndProc)
    return WndProc


def un_hook(hwnd):
    global original_wnd_proc
    if original_wnd_proc:
        # 恢复原来的窗口过程
        SetWindowLongPtr(hwnd, win32con.GWL_WNDPROC, WNDPROC(original_wnd_proc))
        original_wnd_proc = None
        debug(f"卸载钩子并恢复原来的窗口过程: {hwnd}")
        return True
    else:
        debug("未找到可卸载的钩子。")
        return False


# 通过 pid 获取 hwnd 的函数
def get_hwnd_by_pid(pid):
    hwnds = []

    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, hwnds)
    return hwnds


# 示例用法
if __name__ == "__main__":
    hwnds = get_hwnd_by_pid(os.getpid())
    if hwnds:
        hwnd = hwnds[0]
        wnd_proc = set_hook(hwnd)
        debug(f"挂钩设置在 hwnd 上: {hwnd}")

        # 向窗口发送自定义消息
        ctypes.windll.user32.PostMessageW(hwnd, win32con.WM_USER + 128, 0, 12345)

        # 保持消息循环运行以处理钩子
        while not exit_flag:
            win32gui.PumpWaitingMessages()

        if un_hook(hwnd):
            debug("已成功取消挂钩窗口过程。")
        else:
            debug("无法解开窗口过程。")
    else:
        debug("未找到指定 PID 的窗口。")
