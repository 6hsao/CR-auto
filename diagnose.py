"""
诊断脚本 - 分析当前屏幕状态
"""
import sys
sys.path.insert(0, '.')

from core.device import DeviceController
from core.screen import ScreenCapture
from core.detector import GameStateDetector, GamePhase
import numpy as np
from PIL import Image

def analyze_screen():
    device = DeviceController(device_id="emulator-5554", window_name="雷电模拟器")
    screen = ScreenCapture(device, use_window_capture=False)

    screenshot = screen.get_screen(force_refresh=True)
    if screenshot is None:
        print("[FAIL] 无法获取截图")
        return

    print(f"截图尺寸: {screenshot.size}")
    img_array = np.array(screenshot)

    print("\n=== 屏幕区域分析 ===")

    top_region = img_array[0:100, :, :]
    mean_top = np.mean(top_region, axis=(0, 1))
    print(f"顶部区域(0-100)平均颜色: R={mean_top[0]:.1f}, G={mean_top[1]:.1f}, B={mean_top[2]:.1f}")

    upper_region = img_array[100:400, :, :]
    mean_upper = np.mean(upper_region, axis=(0, 1))
    print(f"上部区域(100-400)平均颜色: R={mean_upper[0]:.1f}, G={mean_upper[1]:.1f}, B={mean_upper[2]:.1f}")

    middle_region = img_array[400:900, :, :]
    mean_middle = np.mean(middle_region, axis=(0, 1))
    print(f"中部区域(400-900)平均颜色: R={mean_middle[0]:.1f}, G={mean_middle[1]:.1f}, B={mean_middle[2]:.1f}")

    bottom_region = img_array[1000:1280, :, :]
    mean_bottom = np.mean(bottom_region, axis=(0, 1))
    print(f"底部区域(1000-1280)平均颜色: R={mean_bottom[0]:.1f}, G={mean_bottom[1]:.1f}, B={mean_bottom[2]:.1f}")

    print("\n=== 使用状态检测器 ===")
    detector = GameStateDetector()
    phase = detector.detect_phase(screenshot)
    print(f"检测到的状态: {phase}")

    state = detector.detect_state(screenshot)
    print(f"  圣水: {state.elixir}")
    print(f"  我方皇冠: {state.my_crowns}")
    print(f"  敌方皇冠: {state.enemy_crowns}")

    print("\n=== 大厅特征检测 ===")
    if mean_top[0] > 30 and mean_top[0] < 80 and mean_top[1] < 70 and mean_top[2] > 60:
        print("-> 检测到皇室战争典型深蓝色顶部 [可能是大厅]")
    if mean_upper[0] > 40 and mean_upper[2] > 100:
        print("-> 上部区域有蓝色调 [可能是游戏内容]")
    if np.std(middle_region) > 20:
        print("-> 中部区域有丰富变化 [可能有游戏画面]")
    else:
        print("-> 中部区域较为单一 [可能无游戏内容]")

    print("\n=== 保存诊断截图 ===")
    screenshot.save("diagnostic_screenshot.png")
    print("已保存: diagnostic_screenshot.png")

if __name__ == "__main__":
    analyze_screen()
