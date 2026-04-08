"""
更详细的窗口诊断
"""
import sys
sys.path.insert(0, '.')

try:
    import win32gui
    import win32ui
    import win32con
    import win32api
except ImportError:
    print("win32模块不可用")
    sys.exit(1)

from PIL import Image
import numpy as np

def diagnose_window():
    window_name = "雷电模拟器"
    hWnd = win32gui.FindWindow(0, window_name)
    if hWnd == 0:
        print(f"未找到窗口: {window_name}")
        return

    print(f"窗口句柄: {hWnd}")

    rect = win32gui.GetWindowRect(hWnd)
    print(f"窗口矩形: {rect}")
    print(f"窗口尺寸: 宽={rect[2]-rect[0]}, 高={rect[3]-rect[1]}")

    left, top, right, bottom = rect
    width = right - left
    height = bottom - top

    hWndDC = win32gui.GetWindowDC(hWnd)
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = saveBitMap.GetInfo()
    print(f"Bitmap尺寸: {bmpinfo['bmWidth']} x {bmpinfo['bmHeight']}")

    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX')

    img_array = np.array(img)

    print(f"\n原始窗口截图分析:")
    print(f"  尺寸: {img.size}")
    print(f"  顶部中间颜色: R={img_array[10, width//2, 0]}, G={img_array[10, width//2, 1]}, B={img_array[10, width//2, 2]}")
    print(f"  中心颜色: R={img_array[height//2, width//2, 0]}, G={img_array[height//2, width//2, 1]}, B={img_array[height//2, width//2, 2]}")
    print(f"  底部中间颜色: R={img_array[height-10, width//2, 0]}, G={img_array[height-10, width//2, 1]}, B={img_array[height-10, width//2, 2]}")

    img.save("window_raw.png")
    print("\n已保存原始窗口截图: window_raw.png")

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hWnd, hWndDC)

    print("\n=== 尝试检测游戏区域 ===")
    img_gray = np.mean(img_array, axis=2)
    non_black_rows = np.where(np.mean(img_gray, axis=1) > 5)[0]
    if len(non_black_rows) > 0:
        print(f"非黑色行范围: {non_black_rows[0]} - {non_black_rows[-1]}")
        print(f"非黑色行占比: {len(non_black_rows) / height * 100:.1f}%")
    non_black_cols = np.where(np.mean(img_gray, axis=0) > 5)[0]
    if len(non_black_cols) > 0:
        print(f"非黑色列范围: {non_black_cols[0]} - {non_black_cols[-1]}")
        print(f"非黑色列占比: {len(non_black_cols) / width * 100:.1f}%")

if __name__ == "__main__":
    diagnose_window()
