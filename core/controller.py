import time
from typing import Optional, Tuple, List

from .device import DeviceController
from .screen import ScreenCapture
from .detector import GameStateDetector, GameState, GamePhase
from utils import setup_logger

logger = setup_logger(__name__)


class GameController:
    """游戏控制器，整合设备、截图和检测"""

    SCREEN_RESOLUTION = (720, 1280)

    CARD_POSITIONS = [
        (120, 1150),
        (240, 1150),
        (360, 1150),
        (480, 1150),
    ]

    BATTLEFIELD_LEFT = 360
    BATTLEFIELD_TOP = 300
    BATTLEFIELD_RIGHT = 680
    BATTLEFIELD_BOTTOM = 1000

    def __init__(self, device: DeviceController, detector: GameStateDetector):
        self.device = device
        self.detector = detector
        self.screen = ScreenCapture(device, use_window_capture=False)
        self.last_action_time = 0
        self.action_cooldown = 0.3

    def refresh_screen(self) -> None:
        """刷新屏幕"""
        self.screen.get_screen(force_refresh=True)

    def get_game_state(self) -> GameState:
        """获取当前游戏状态"""
        screenshot = self.screen.get_screen()
        if screenshot:
            return self.detector.detect_state(screenshot)
        return GameState(phase=GamePhase.UNKNOWN)

    def wait_for_phase(self, target_phase: GamePhase, timeout: float = 30.0) -> bool:
        """等待进入目标阶段"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            state = self.get_game_state()
            if state.phase == target_phase:
                return True
            time.sleep(0.5)
        return False

    def tap_play_button(self) -> bool:
        """点击开始游戏按钮"""
        play_button_pos = (360, 950)
        return self.device.tap(*play_button_pos)

    def tap_battle_mode(self, mode: str = "2v2") -> bool:
        """选择战斗模式"""
        if mode == "1v1":
            pos = (360, 400)
        elif mode == "2v2":
            pos = (360, 550)
        else:
            pos = (360, 700)
        return self.device.tap(*pos)

    def tap_deck_confirm(self) -> bool:
        """确认卡组"""
        confirm_pos = (550, 1150)
        return self.device.tap(*confirm_pos)

    def place_card(self, card_index: int, target_x: int, target_y: int) -> bool:
        """出牌操作：先点击手牌，再点击战场位置"""
        if card_index < 0 or card_index >= len(self.CARD_POSITIONS):
            logger.warning(f"无效的卡牌索引: {card_index}")
            return False

        if time.time() - self.last_action_time < self.action_cooldown:
            time.sleep(self.action_cooldown)

        card_pos = self.CARD_POSITIONS[card_index]
        self.device.tap(*card_pos, duration=50)
        time.sleep(0.1)
        self.device.tap(target_x, target_y, duration=100)

        self.last_action_time = time.time()
        logger.debug(f"出牌: 卡牌{card_index} -> 位置({target_x}, {target_y})")
        return True

    def drag_card(self, card_index: int, target_x: int, target_y: int) -> bool:
        """拖拽出牌"""
        if card_index < 0 or card_index >= len(self.CARD_POSITIONS):
            return False

        card_pos = self.CARD_POSITIONS[card_index]

        self.device.swipe(card_pos[0], card_pos[1], target_x, target_y, duration=300)
        logger.debug(f"拖拽出牌: 卡牌{card_index} -> 位置({target_x}, {target_y})")
        return True

    def tap_ok_button(self) -> bool:
        """点击确定按钮（如对战结束的确认）"""
        ok_pos = (360, 1150)
        # 顺便点一下屏幕中间，防止卡在展示动画
        self.device.tap(360, 600, duration=50)
        time.sleep(0.5)
        return self.device.tap(*ok_pos)

    def tap_next_button(self) -> bool:
        """点击下一步按钮"""
        next_pos = (550, 1100)
        return self.device.tap(*next_pos)

    def tap_back_button(self) -> bool:
        """点击返回按钮"""
        back_pos = (50, 50)
        return self.device.tap(*back_pos)

    def exit_to_lobby(self) -> bool:
        """退出到大厅"""
        for _ in range(3):
            self.device.press_back()
            time.sleep(0.5)

        state = self.get_game_state()
        if state.phase != GamePhase.LOBBY:
            return False
        return True

    def collect_chest(self) -> bool:
        """领取宝箱"""
        collect_pos = (360, 800)
        return self.device.tap(*collect_pos)

    def skip_chest_timer(self) -> bool:
        """跳过宝箱时间（用宝石）"""
        skip_pos = (550, 650)
        return self.device.tap(*skip_pos)

    def find_and_tap(self, target_color: Tuple[int, int, int], region: Tuple[int, int, int, int],
                     tolerance: int = 30) -> bool:
        """在指定区域查找并点击指定颜色"""
        screenshot = self.screen.get_screen(force_refresh=True)
        if not screenshot:
            return False

        import numpy as np

        region_img = screenshot.crop(region)
        img_array = np.array(region_img)

        target = np.array(target_color)
        mask = np.all(np.abs(img_array.astype(int) - target) < tolerance, axis=2)
        positions = np.where(mask)

        if len(positions[0]) > 0:
            y, x = positions[0][0], positions[1][0]
            abs_x = region[0] + x
            abs_y = region[1] + y
            return self.device.tap(abs_x, abs_y)

        return False
