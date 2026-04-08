import time
from typing import Optional, Tuple
from PIL import Image

from utils import setup_logger

logger = setup_logger(__name__)


class ScreenCapture:
    """屏幕截图管理 - 仅用于状态检测，不保存文件"""

    def __init__(self, device_controller, use_window_capture: bool = True):
        self.device = device_controller
        self.use_window_capture = use_window_capture
        self.last_screenshot: Optional[Image.Image] = None
        self.last_capture_time: float = 0
        self.capture_interval: float = 0.1

    def get_screen(self, force_refresh: bool = False) -> Optional[Image.Image]:
        """获取当前屏幕截图"""
        current_time = time.time()

        if not force_refresh and self.last_screenshot is not None:
            if current_time - self.last_capture_time < self.capture_interval:
                return self.last_screenshot

        if self.use_window_capture:
            screenshot = self.device.screenshot_window()
        else:
            screenshot = self.device.screenshot()

        if screenshot:
            self.last_screenshot = screenshot
            self.last_capture_time = current_time

        return screenshot

    def get_game_area(self, crop_box: Tuple[int, int, int, int] = (0, 30, 720, 1200)) -> Optional[Image.Image]:
        """获取裁剪后的游戏区域"""
        screen = self.get_screen()
        if screen:
            return screen.crop(crop_box)
        return None
