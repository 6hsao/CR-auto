"""
窗口诊断 - 检查模拟器窗口位置
"""
import sys
sys.path.insert(0, '.')

try:
    import win32gui
    import win32ui
    import win32con
except ImportError:
    print("win32模块不可用")
    sys.exit(1)

def find_window():
    window_names = ["雷电模拟器", "雷电模拟器 HD", "BlueStacks", "LDPlayer"]

    for name in window_names:
        hWnd = win32gui.FindWindow(0, name)
        if hWnd != 0:
            print(f"找到窗口: {name} (句柄: {hWnd})")
            rect = win32gui.GetWindowRect(hWnd)
            print(f"  窗口位置: 左={rect[0]}, 上={rect[1]}, 右={rect[2]}, 下={rect[3]}")
            print(f"  窗口尺寸: 宽={rect[2]-rect[0]}, 高={rect[3]-rect[1]}")
            return hWnd

    print("未找到模拟器窗口")

    print("\n所有顶级窗口:")
    def enum_handler(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if title:
            results.append((hwnd, title))
    windows = []
    win32gui.EnumWindows(lambda h, w: enum_handler(h, w) or w.append(h), windows)
    for hwnd, title in windows[:20]:
        print(f"  {title} (hwnd={hwnd})")

    return None

if __name__ == "__main__":
    find_window()
