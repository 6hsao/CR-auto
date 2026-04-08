import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np

from utils import setup_logger

logger = setup_logger(__name__)


class GamePhase(Enum):
    """游戏阶段枚举"""
    UNKNOWN = "unknown"
    LOBBY = "lobby"
    MODE_SELECT = "mode_select"
    DECK_SELECT = "deck_select"
    MATCHING = "matching"
    BATTLE_PREPARE = "battle_prepare"
    BATTLE = "battle"
    BATTLE_END = "battle_end"
    RESULT = "result"
    ERROR = "error"


@dataclass
class GameState:
    """游戏状态数据类"""
    phase: GamePhase = GamePhase.UNKNOWN
    battle_time: int = 0
    my_crowns: int = 0
    enemy_crowns: int = 0
    left_tower_hp: int = 100
    right_tower_hp: int = 100
    hand_cards: List[int] = None
    elixir: int = 5

    def __post_init__(self):
        if self.hand_cards is None:
            self.hand_cards = []


class GameStateDetector:
    """游戏状态检测器（简化版，基于颜色/特征检测）"""

    CROP_BATTLE_AREA = (50, 200, 670, 1100)
    CROP_LOBBY_TOP = (0, 0, 720, 100)
    CROP_BATTLE_UI = (0, 1000, 720, 1280)

    LOBBY_COLORS = {
        "play_button": [(255, 200, 50), (280, 220, 60)],
        "battle_mode": [(100, 180, 255), (120, 200, 275)],
    }

    BATTLE_COLORS = {
        "elixir": [(230, 130, 30), (250, 150, 50)],
        "crown": [(255, 215, 0), (275, 235, 20)],
        "tower_damage": [(255, 50, 50), (275, 70, 70)],
    }

    def __init__(self):
        self.last_phase = GamePhase.UNKNOWN
        self.phase_change_time = time.time()
        self.battle_start_time: Optional[float] = None

    def detect_phase(self, screenshot: Image.Image) -> GamePhase:
        """检测游戏阶段"""
        img_array = np.array(screenshot)

        if self._is_lobby(img_array):
            return GamePhase.LOBBY
        elif self._is_matching(img_array):
            return GamePhase.MATCHING
        elif self._is_battle(img_array):
            return GamePhase.BATTLE
        elif self._is_battle_end(img_array):
            return GamePhase.BATTLE_END
        elif self._is_deck_select(img_array):
            return GamePhase.DECK_SELECT
        else:
            return GamePhase.UNKNOWN

    def _is_lobby(self, img_array: np.ndarray) -> bool:
        """检测是否在大厅"""
        # 大厅特有的黄色“对战”按钮区域
        button_region = img_array[900:1020, 250:470, :]
        yellow_target = np.array([255, 200, 50])
        diff = np.abs(button_region.astype(int) - yellow_target)
        mask = np.all(diff < 80, axis=2)
        # 如果黄色像素占比较大，说明是对战按钮
        if np.sum(mask) > 10000:
            return True
            
        return False

    def _is_matching(self, img_array: np.ndarray) -> bool:
        """检测是否在匹配中"""
        # 匹配中会有一个红色的取消按钮
        cancel_btn_region = img_array[1000:1100, 250:470, :]
        red_target = np.array([220, 50, 50])
        diff = np.abs(cancel_btn_region.astype(int) - red_target)
        mask = np.all(diff < 60, axis=2)
        if np.sum(mask) > 5000:
            return True
        return False

    def _is_battle(self, img_array: np.ndarray) -> bool:
        """检测是否在战斗中"""
        # 战斗中的圣水条是紫红色/粉红色 (R高, B高)
        bottom_region = img_array[1150:1250, 100:600, :]
        elixir_target = np.array([220, 50, 200]) # 圣水的粉紫颜色
        diff = np.abs(bottom_region.astype(int) - elixir_target)
        mask = np.all(diff < 80, axis=2)
        if np.sum(mask) > 1000: # 只要检测到粉色圣水条特征即可
            return True
        return False

    def _is_battle_end(self, img_array: np.ndarray) -> bool:
        """检测是否在战斗结束界面"""
        center_region = img_array[300:700, 150:570, :]
        mean_color = np.mean(center_region, axis=(0, 1))
        if mean_color[0] > 200 and mean_color[1] > 180 and mean_color[2] > 150:
            return True
        return False

    def _is_deck_select(self, img_array: np.ndarray) -> bool:
        """检测是否在选卡界面"""
        left_region = img_array[200:1000, 0:100, :]
        mean_color = np.mean(left_region, axis=(0, 1))
        if mean_color[0] > 100 and mean_color[1] > 80 and mean_color[2] > 60:
            return True
        return False

    def detect_state(self, screenshot: Image.Image) -> GameState:
        """检测完整游戏状态"""
        img_array = np.array(screenshot)
        phase = self.detect_phase(screenshot)

        state = GameState(phase=phase)

        if phase == GamePhase.BATTLE:
            if self.battle_start_time is None:
                self.battle_start_time = time.time()
            state.battle_time = int(time.time() - self.battle_start_time)

            state.elixir = self._detect_elixir(img_array)
            state.my_crowns, state.enemy_crowns = self._detect_crowns(img_array)

        elif phase in [GamePhase.BATTLE_END, GamePhase.RESULT]:
            if self.battle_start_time is not None:
                state.battle_time = int(time.time() - self.battle_start_time)
                self.battle_start_time = None

            state.my_crowns, state.enemy_crowns = self._detect_crowns(img_array)

        elif phase == GamePhase.LOBBY:
            self.battle_start_time = None

        return state

    def _detect_elixir(self, img_array: np.ndarray) -> int:
        """检测圣水数量（简化版）"""
        elixir_region = img_array[1050:1150, 330:400, :]
        mean_color = np.mean(elixir_region, axis=(0, 1))

        if 220 < mean_color[0] < 255 and 120 < mean_color[1] < 160 and 20 < mean_color[2] < 50:
            return 10

        return int(np.mean(elixir_region) / 25)

    def _detect_crowns(self, img_array: np.ndarray) -> Tuple[int, int]:
        """检测皇冠数量"""
        my_crown = 0
        enemy_crown = 0

        left_area = img_array[50:150, 50:150, :]
        if np.mean(left_area[:, :, 0]) > 200 and np.mean(left_area[:, :, 1]) > 180:
            my_crown = 1
        if np.mean(left_area[:, :, 0]) > 230 and np.mean(left_area[:, :, 1]) > 200:
            my_crown = 2
        if np.mean(left_area[:, :, 0]) > 250 and np.mean(left_area[:, :, 1]) > 220:
            my_crown = 3

        right_area = img_array[50:150, 570:670, :]
        if np.mean(right_area[:, :, 0]) > 200 and np.mean(right_area[:, :, 1]) > 180:
            enemy_crown = 1
        if np.mean(right_area[:, :, 0]) > 230 and np.mean(right_area[:, :, 1]) > 200:
            enemy_crown = 2
        if np.mean(right_area[:, :, 0]) > 250 and np.mean(right_area[:, :, 1]) > 220:
            enemy_crown = 3

        return my_crown, enemy_crown

    def reset(self) -> None:
        """重置检测器状态"""
        self.last_phase = GamePhase.UNKNOWN
        self.battle_start_time = None
