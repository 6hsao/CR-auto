"""
皇室战争自动对战脚本
Clash Royale Auto Battle Script

功能：
- 自动进入游戏
- 自动匹配对战
- 自动出牌
- 自动循环继续
"""

__version__ = "0.1.0"
__author__ = "Auto Developer"

from .core import DeviceController, ScreenCapture, GameStateDetector, GamePhase, GameController
from .tasks import BaseTask, TaskStatus, BattleTask
from .game import GameState, BattleManager

__all__ = [
    'DeviceController',
    'ScreenCapture',
    'GameStateDetector',
    'GamePhase',
    'GameController',
    'BaseTask',
    'TaskStatus',
    'BattleTask',
    'GameState',
    'BattleManager',
]
