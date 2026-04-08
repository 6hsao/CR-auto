from dataclasses import dataclass, field
from typing import List, Optional
import time
import logging

from core.detector import GamePhase


@dataclass
class GameState:
    """游戏状态数据类"""
    phase: GamePhase = GamePhase.UNKNOWN
    battle_time: int = 0
    my_crowns: int = 0
    enemy_crowns: int = 0
    left_tower_hp: int = 100
    right_tower_hp: int = 100
    hand_cards: List[int] = field(default_factory=list)
    elixir: int = 5

    def is_battle_active(self) -> bool:
        """是否在战斗中"""
        return self.phase == GamePhase.BATTLE

    def is_in_lobby(self) -> bool:
        """是否在大厅"""
        return self.phase == GamePhase.LOBBY

    def get_win_result(self) -> Optional[str]:
        """获取战斗结果"""
        if self.phase == GamePhase.RESULT or self.phase == GamePhase.BATTLE_END:
            if self.my_crowns > self.enemy_crowns:
                return "WIN"
            elif self.my_crowns < self.enemy_crowns:
                return "LOSE"
            else:
                return "DRAW"
        return None


class BattleManager:
    """战斗管理器"""

    def __init__(self):
        self.current_state: Optional[GameState] = None
        self.battle_history: List[dict] = []
        self.battles_won = 0
        self.battles_lost = 0
        self.battles_draw = 0
        self.current_battle_start: Optional[float] = None

    def start_battle(self) -> None:
        """标记战斗开始"""
        self.current_battle_start = time.time()
        logger.info("战斗开始")

    def end_battle(self, result: str, my_crowns: int, enemy_crowns: int) -> None:
        """标记战斗结束"""
        if self.current_battle_start:
            duration = time.time() - self.current_battle_start
            self.current_battle_start = None

            battle_record = {
                "result": result,
                "my_crowns": my_crowns,
                "enemy_crowns": enemy_crowns,
                "duration": int(duration),
                "timestamp": time.time(),
            }
            self.battle_history.append(battle_record)

            if result == "WIN":
                self.battles_won += 1
            elif result == "LOSE":
                self.battles_lost += 1
            else:
                self.battles_draw += 1

            logger.info(f"战斗结束: {result} | {my_crowns} vs {enemy_crowns} | 时长: {int(duration)}s")

    def get_stats(self) -> dict:
        """获取战斗统计"""
        total = self.battles_won + self.battles_lost + self.battles_draw
        win_rate = self.battles_won / total if total > 0 else 0

        return {
            "total": total,
            "won": self.battles_won,
            "lost": self.battles_lost,
            "draw": self.battles_draw,
            "win_rate": win_rate,
        }

    def reset(self) -> None:
        """重置统计"""
        self.battles_won = 0
        self.battles_lost = 0
        self.battles_draw = 0
        self.battle_history.clear()


logger = logging.getLogger(__name__)
