import os
import subprocess
import shutil
from typing import Optional, Tuple
from PIL import Image
import time

try:
    import win32gui
    import win32ui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from utils import setup_logger, get_project_root

logger = setup_logger(__name__)


class DeviceController:
    """设备交互控制器，支持模拟器和真机"""

    def __init__(self, device_id: str = "127.0.0.1:5555", window_name: str = "雷电模拟器"):
        self.device_id = device_id
        self.window_name = window_name
        self._adb_path: Optional[str] = None
        self._setup_adb()

    def _setup_adb(self) -> None:
        """配置ADB路径"""
        candidates = [
            os.path.join(os.environ.get("LDPLAYER_HOME", ""), "adb.exe"),
            r"D:\leidian\LDPlayer9\adb.exe",
            r"C:\leidian\LDPlayer9\adb.exe",
            r"C:\leidian\LDPlayer\adb.exe",
            r"C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
            r"C:\Program Files\LDPlayer\LDPlayer4.0\adb.exe",
        ]
        for adb_path in candidates:
            if adb_path and os.path.isfile(adb_path):
                self._adb_path = adb_path
                os.environ["ADB"] = adb_path
                os.environ["PATH"] = os.path.dirname(adb_path) + os.pathsep + os.environ.get("PATH", "")
                logger.info(f"使用ADB: {adb_path}")
                return

        adb_in_path = shutil.which("adb")
        if adb_in_path:
            self._adb_path = adb_in_path
            logger.info(f"使用PATH中的ADB: {adb_in_path}")
        else:
            logger.warning("未找到ADB，请确保adb在PATH中")

    def _run_adb(self, *args) -> subprocess.CompletedProcess:
        """执行ADB命令"""
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def screenshot(self) -> Optional[Image.Image]:
        """通过ADB截图"""
        try:
            self._run_adb("shell", "screencap", "-p", "/sdcard/screenshot.png")
            self._run_adb("pull", "/sdcard/screenshot.png", str(get_project_root() / "temp_screenshot.png"))
            img = Image.open(str(get_project_root() / "temp_screenshot.png"))
            if img.mode == "RGBA":
                img = img.convert("RGB")
            return img
        except Exception as e:
            logger.error(f"ADB截图失败: {e}")
            return None

    def screenshot_window(self, crop_box: Tuple[int, int, int, int] = None) -> Optional[Image.Image]:
        """窗口截图（Windows模拟器）- 自动适配雷电模拟器竖屏"""
        if not WIN32_AVAILABLE:
            logger.warning("win32gui不可用")
            return None

        try:
            hWnd = win32gui.FindWindow(0, self.window_name)
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "雷电模拟器")
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "BlueStacks")

            if hWnd == 0:
                logger.error(f"未找到窗口: {self.window_name}")
                return None

            left, top, right, bottom = win32gui.GetWindowRect(hWnd)
            window_width = right - left
            window_height = bottom - top

            hWndDC = win32gui.GetWindowDC(hWnd)
            mfcDC = win32ui.CreateDCFromHandle(hWndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, window_width, window_height)
            saveDC.SelectObject(saveBitMap)
            saveDC.BitBlt((0, 0), (window_width, window_height), mfcDC, (0, 0), win32con.SRCCOPY)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX')

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hWnd, hWndDC)

            game_width = 720
            game_height = 1280

            if window_width < window_height:
                cropped = im_PIL.resize((game_width, game_height), Image.Resampling.LANCZOS)
            else:
                cropped = im_PIL

            if crop_box:
                cropped = cropped.crop(crop_box)

            return cropped

        except Exception as e:
            logger.error(f"窗口截图失败: {e}")
            return None

    def tap(self, x: int, y: int, duration: int = 50) -> bool:
        """点击指定坐标"""
        if self._adb_path and os.path.exists(self._adb_path):
            try:
                self._run_adb("shell", "input", "tap", str(x), str(y))
                logger.debug(f"点击: ({x}, {y}) [ADB]")
                return True
            except Exception as e:
                logger.error(f"ADB点击失败: {e}")

        if WIN32_AVAILABLE:
            return self._win32_tap(x, y)
        else:
            logger.error("无法执行点击操作")
            return False

    def _win32_tap(self, x: int, y: int) -> bool:
        """Windows模拟器点击"""
        try:
            hWnd = win32gui.FindWindow(0, self.window_name)
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "雷电模拟器")
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "BlueStacks")

            if hWnd == 0:
                logger.error("未找到模拟器窗口")
                return False

            left, top, right, bottom = win32gui.GetWindowRect(hWnd)

            screen_x = left + x
            screen_y = top + y

            win32api.SetCursorPos((screen_x, screen_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

            logger.debug(f"点击: ({x}, {y}) [Win32]")
            return True
        except Exception as e:
            logger.error(f"Win32点击失败: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """滑动操作"""
        if self._adb_path and os.path.exists(self._adb_path):
            try:
                self._run_adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration))
                logger.debug(f"滑动: ({x1},{y1}) -> ({x2},{y2}) [ADB]")
                return True
            except Exception as e:
                logger.error(f"ADB滑动失败: {e}")

        if WIN32_AVAILABLE:
            return self._win32_swipe(x1, y1, x2, y2, duration)
        else:
            logger.error("无法执行滑动操作")
            return False

    def _win32_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Windows模拟器滑动"""
        try:
            hWnd = win32gui.FindWindow(0, self.window_name)
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "雷电模拟器")
            if hWnd == 0:
                hWnd = win32gui.FindWindow(0, "BlueStacks")

            if hWnd == 0:
                logger.error("未找到模拟器窗口")
                return False

            left, top, right, bottom = win32gui.GetWindowRect(hWnd)

            screen_x1 = left + x1
            screen_y1 = top + y1
            screen_x2 = left + x2
            screen_y2 = top + y2

            steps = max(1, int(duration / 10))
            for i in range(steps + 1):
                t = i / steps
                current_x = int(screen_x1 + (screen_x2 - screen_x1) * t)
                current_y = int(screen_y1 + (screen_y2 - screen_y1) * t)
                win32api.SetCursorPos((current_x, current_y))
                if i == 0:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(duration / steps / 1000)

            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            logger.debug(f"滑动: ({x1},{y1}) -> ({x2},{y2}) [Win32]")
            return True
        except Exception as e:
            logger.error(f"Win32滑动失败: {e}")
            return False

    def long_press(self, x: int, y: int, duration: int = 1000) -> bool:
        """长按操作"""
        return self.swipe(x, y, x, y, duration)

    def press_back(self) -> bool:
        """按返回键"""
        try:
            self._run_adb("shell", "input", "keyevent", "KEYCODE_BACK")
            return True
        except Exception as e:
            logger.error(f"返回键失败: {e}")
            return False

    def press_home(self) -> bool:
        """按Home键"""
        try:
            self._run_adb("shell", "input", "keyevent", "KEYCODE_HOME")
            return True
        except Exception as e:
            logger.error(f"Home键失败: {e}")
            return False

    def start_app(self, package_name: str = "com.supercell.clashroyale") -> bool:
        """启动应用"""
        try:
            self._run_adb("shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1")
            logger.info(f"启动应用: {package_name}")
            return True
        except Exception as e:
            logger.error(f"启动应用失败: {e}")
            return False

    def stop_app(self, package_name: str = "com.supercell.clashroyale") -> bool:
        """停止应用"""
        try:
            self._run_adb("shell", "am", "force-stop", package_name)
            logger.info(f"停止应用: {package_name}")
            return True
        except Exception as e:
            logger.error(f"停止应用失败: {e}")
            return False

    def is_device_connected(self) -> bool:
        """检查设备连接状态"""
        try:
            result = self._run_adb("shell", "getprop", "ro.build.version.release")
            return result.returncode == 0
        except Exception:
            return False
