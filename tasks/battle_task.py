import time
import random
from typing import Optional, List, Tuple

from .base_task import BaseTask, TaskStatus
from game.game_state import BattleManager
from core.controller import GameController
from core.detector import GamePhase
from utils import setup_logger

logger = setup_logger(__name__)


class BattleTask(BaseTask):
    """自动对战任务"""

    def __init__(self, controller: GameController, config: dict = None):
        super().__init__("BattleTask", priority=0)
        self.controller = controller
        self.config = config or {}

        self.max_battles = self.config.get("max_battles", 10)
        self.battle_mode = self.config.get("battle_mode", "1v1")
        self.auto_restart = self.config.get("auto_restart", True)
        self.strategy = self.config.get("strategy", "aggressive")

        self.battle_manager = BattleManager()
        self.current_battle_count = 0
        self.deck_index = self.config.get("deck_index", 0)

        self.last_card_played = 0
        self.min_elixir_to_play = 4

    def check_preconditions(self) -> bool:
        """检查前置条件"""
        return True

    def execute(self) -> bool:
        """执行对战任务"""
        logger.info(f"开始自动对战任务 (模式: {self.battle_mode}, 最大场次: {self.max_battles})")
        
        unknown_count = 0

        while self.current_battle_count < self.max_battles:
            state = self.controller.get_game_state()

            if state.phase == GamePhase.LOBBY:
                unknown_count = 0
                self._handle_lobby()
            elif state.phase == GamePhase.MATCHING:
                unknown_count = 0
                self._handle_matching()
            elif state.phase == GamePhase.DECK_SELECT:
                unknown_count = 0
                self._handle_deck_select()
            elif state.phase == GamePhase.BATTLE:
                unknown_count = 0
                self._handle_battle()
            elif state.phase == GamePhase.BATTLE_END:
                unknown_count = 0
                self._handle_battle_end()
            elif state.phase == GamePhase.RESULT:
                unknown_count = 0
                self._handle_result()
            else:
                logger.debug(f"未知状态: {state.phase}")
                unknown_count += 1
                if unknown_count > 10:
                    # 尝试点击确认和返回按钮来消除弹窗
                    logger.warning("持续未知状态，尝试清理屏幕...")
                    self.controller.tap_ok_button()
                    self.controller.tap_back_button()
                    time.sleep(2)
                    # 每隔30次未知状态，重置一下计数
                    if unknown_count > 30:
                        unknown_count = 0
                time.sleep(1)

            if self.current_battle_count >= self.max_battles and state.phase == GamePhase.LOBBY:
                logger.info("达到最大场次限制并已返回大厅，结束任务")
                break

        stats = self.battle_manager.get_stats()
        logger.info(f"对战统计: {stats}")
        return True

    def _handle_lobby(self) -> None:
        """处理大厅状态"""
        logger.info("当前在大厅，准备开始匹配...")
        self.controller.tap_play_button()
        time.sleep(1)

    def _handle_matching(self) -> None:
        """处理匹配中状态"""
        logger.info("正在匹配中...")
        timeout = 60
        start = time.time()

        while time.time() - start < timeout:
            state = self.controller.get_game_state()
            if state.phase != GamePhase.MATCHING:
                break
            time.sleep(2)

        if state.phase == GamePhase.MATCHING:
            logger.warning("匹配超时，返回大厅重试")
            self.controller.tap_back_button()
            time.sleep(1)

    def _handle_deck_select(self) -> None:
        """处理选卡阶段"""
        logger.info("选卡阶段...")
        self.controller.tap_deck_confirm()
        time.sleep(0.5)
        # 不要在这里增加 current_battle_count，在战斗结束时再增加
        self.battle_manager.start_battle()
        logger.info("战斗即将开始")

    def _handle_battle(self) -> None:
        """处理战斗状态"""
        state = self.controller.get_game_state()

        if self.strategy == "aggressive":
            self._aggressive_strategy(state)
        elif self.strategy == "defensive":
            self._defensive_strategy(state)
        else:
            self._random_strategy(state)

        time.sleep(0.5)

    def _aggressive_strategy(self, state) -> None:
        """激进策略：我方最中间连下两张牌，优先 5 费牌"""
        # 我方最中间位置（战场中间区域，不是最底部）
        target_x = random.randint(300, 420)
        target_y = random.randint(700, 850)
        
        # 优先选择 5 费牌（假设索引 0 是 5 费，从左到右费用递减）
        def find_best_card(prefer_high_cost: bool = True) -> int:
            """优先选择高费牌（5 费）"""
            if prefer_high_cost and state.hand_cards:
                # 优先选择最左边的牌（假设是 5 费）
                for i in range(4):
                    if i < len(state.hand_cards):
                        return i
            return random.randint(0, min(3, len(state.hand_cards) - 1)) if state.hand_cards else random.randint(0, 3)
        
        # 有费用就连下两张牌
        if state.elixir >= 4:
            # 下第一张牌（优先 5 费）
            card_index1 = find_best_card(True)
            self.controller.place_card(card_index1, target_x, target_y)
            time.sleep(0.3)
            
            # 下第二张牌（不同位置）
            card_index2 = find_best_card(False)
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            self.controller.place_card(card_index2, target_x + offset_x, target_y + offset_y)
            time.sleep(random.uniform(1.0, 2.0))
        else:
            # 费用不够也下一张（优先 5 费）
            card_index = find_best_card(True)
            self.controller.place_card(card_index, target_x, target_y)
            time.sleep(random.uniform(1.0, 2.0))

    def _defensive_strategy(self, state) -> None:
        """防守策略：我方最中间连下两张牌，优先 5 费牌"""
        # 我方最中间位置（战场中间区域）
        target_x = random.randint(300, 420)
        target_y = random.randint(700, 850)
        
        # 优先选择 5 费牌（假设索引 0 是 5 费）
        def find_best_card(prefer_high_cost: bool = True) -> int:
            """优先选择高费牌（5 费）"""
            if prefer_high_cost and state.hand_cards:
                for i in range(4):
                    if i < len(state.hand_cards):
                        return i
            return random.randint(0, min(3, len(state.hand_cards) - 1)) if state.hand_cards else random.randint(0, 3)
        
        # 有费用就连下两张牌
        if state.elixir >= 4:
            # 下第一张牌（优先 5 费）
            card_index1 = find_best_card(True)
            self.controller.place_card(card_index1, target_x, target_y)
            time.sleep(0.3)
            
            # 下第二张牌
            card_index2 = find_best_card(False)
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            self.controller.place_card(card_index2, target_x + offset_x, target_y + offset_y)
            time.sleep(random.uniform(1.0, 2.0))

    def _random_strategy(self, state) -> None:
        """随机策略：我方最中间连下两张牌，优先 5 费牌"""
        # 我方最中间位置（战场中间区域）
        target_x = random.randint(300, 420)
        target_y = random.randint(700, 850)
        
        # 优先选择 5 费牌（假设索引 0 是 5 费）
        def find_best_card(prefer_high_cost: bool = True) -> int:
            """优先选择高费牌（5 费）"""
            if prefer_high_cost and state.hand_cards:
                for i in range(4):
                    if i < len(state.hand_cards):
                        return i
            return random.randint(0, min(3, len(state.hand_cards) - 1)) if state.hand_cards else random.randint(0, 3)
        
        # 有费用就连下两张牌
        if state.elixir >= 4 and random.random() > 0.5:
            # 下第一张牌（优先 5 费）
            card_index1 = find_best_card(True)
            self.controller.place_card(card_index1, target_x, target_y)
            time.sleep(0.3)
            
            # 下第二张牌
            card_index2 = find_best_card(False)
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            self.controller.place_card(card_index2, target_x + offset_x, target_y + offset_y)
            time.sleep(random.uniform(1.0, 2.0))

    def _handle_battle_end(self) -> None:
        """处理战斗结束"""
        state = self.controller.get_game_state()
        result = state.get_win_result()

        if result:
            self.battle_manager.end_battle(result, state.my_crowns, state.enemy_crowns)
            logger.info(f"战斗结果: {result} | {state.my_crowns} vs {state.enemy_crowns}")
        else:
            self.battle_manager.end_battle("UNKNOWN", state.my_crowns, state.enemy_crowns)
            logger.info("战斗结果: 未知")
        
        self.current_battle_count += 1
        logger.info(f"完成 {self.current_battle_count}/{self.max_battles} 场对战")

        time.sleep(2)

    def _handle_result(self) -> None:
        """处理结果界面"""
        logger.info("点击继续...")
        self.controller.tap_ok_button()
        time.sleep(1)

        state = self.controller.get_game_state()
        if state.phase == GamePhase.LOBBY:
            logger.info("已返回大厅")

    def stop(self) -> None:
        """停止任务"""
        self.status = TaskStatus.PAUSED
        logger.info("对战任务已停止")

    def get_progress(self) -> dict:
        """获取任务进度"""
        stats = self.battle_manager.get_stats()
        return {
            "current_battle": self.current_battle_count,
            "max_battles": self.max_battles,
            "status": self.status.value,
            "stats": stats,
        }
