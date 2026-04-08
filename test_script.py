"""
快速测试脚本 - 验证脚本功能
"""
import sys
sys.path.insert(0, '.')

from core.device import DeviceController
from core.screen import ScreenCapture
from core.detector import GameStateDetector, GamePhase
import time

def test_window_screenshot():
    """测试窗口截图"""
    print("=" * 50)
    print("测试1: 窗口截图")

    device = DeviceController(window_name="雷电模拟器")
    screen = ScreenCapture(device, use_window_capture=False)

    screenshot = screen.get_screen(force_refresh=True)
    if screenshot:
        print(f"[OK] 截图成功! 尺寸: {screenshot.size}")
        screenshot.save("test_screenshot.png")
        print(f"[OK] 截图已保存: test_screenshot.png")
        return True
    else:
        print("[FAIL] 截图失败")
        return False

def test_adb_screenshot():
    """测试ADB截图"""
    print("\n" + "=" * 50)
    print("测试2: ADB截图")

    device = DeviceController(device_id="emulator-5554")
    screenshot = device.screenshot()
    if screenshot:
        print(f"[OK] ADB截图成功! 尺寸: {screenshot.size}")
        return True
    else:
        print("[FAIL] ADB截图失败 (可能未连接设备)")
        return False

def test_state_detection():
    """测试状态检测"""
    print("\n" + "=" * 50)
    print("测试3: 游戏状态检测")

    device = DeviceController(window_name="雷电模拟器")
    screen = ScreenCapture(device, use_window_capture=True)
    detector = GameStateDetector()

    screenshot = screen.get_screen(force_refresh=True)
    if screenshot:
        state = detector.detect_state(screenshot)
        print(f"检测到的状态: {state.phase.value}")
        print(f"圣水: {state.elixir}")
        print(f"我方皇冠: {state.my_crowns}")
        print(f"敌方皇冠: {state.enemy_crowns}")
        return True
    else:
        print("[FAIL] 状态检测失败")
        return False

def test_device_control():
    """测试设备控制"""
    print("\n" + "=" * 50)
    print("测试4: 设备控制")

    device = DeviceController(window_name="雷电模拟器")
    print("尝试点击 (360, 640)...")
    result = device.tap(360, 640)
    if result:
        print("[OK] 点击成功")
    else:
        print("[FAIL] 点击失败")
    return result

def main():
    print("皇室战争自动对战 - 功能测试")
    print("=" * 50)

    tests = [
        ("窗口截图", test_window_screenshot),
        ("ADB截图", test_adb_screenshot),
        ("状态检测", test_state_detection),
        ("设备控制", test_device_control),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] {name} 测试出错: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"  {name}: {status}")

    passed = sum(1 for _, r in results if r)
    print(f"\n通过: {passed}/{len(results)}")

if __name__ == "__main__":
    main()
