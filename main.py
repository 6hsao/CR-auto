import os
import sys
import argparse
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import DeviceController, GameStateDetector, GameController
from tasks import BattleTask
from game import BattleManager
from utils import setup_logger, get_project_root

logger = setup_logger(__name__, "INFO")


class ClashRoyaleAuto:
    """皇室战争自动对战主类"""

    def __init__(self, device_id: str = "emulator-5554", window_name: str = "雷电模拟器"):
        self.device_id = device_id
        self.window_name = window_name

        self.device = DeviceController(device_id, window_name)
        self.detector = GameStateDetector()
        self.controller = GameController(self.device, self.detector)

        self.running = False
        self.paused = False

    def start(self, max_battles: int = 10, battle_mode: str = "1v1", strategy: str = "aggressive") -> None:
        """启动自动对战"""
        self.running = True

        logger.info("=" * 50)
        logger.info("皇室战争自动对战启动")
        logger.info(f"设备ID: {self.device_id}")
        logger.info(f"窗口名称: {self.window_name}")
        logger.info(f"最大场次: {max_battles}")
        logger.info(f"战斗模式: {battle_mode}")
        logger.info(f"策略: {strategy}")
        logger.info("=" * 50)

        self.controller.refresh_screen()
        time.sleep(1)

        state = self.controller.get_game_state()
        logger.info(f"当前游戏状态: {state.phase}")
        logger.info("开始自动对战流程...")

        config = {
            "max_battles": max_battles,
            "battle_mode": battle_mode,
            "strategy": strategy,
            "auto_restart": True,
            "deck_index": 0,
        }

        task = BattleTask(self.controller, config)

        try:
            task.run()
        except KeyboardInterrupt:
            logger.info("用户中断")
        except Exception as e:
            logger.error(f"发生错误: {e}")
            raise
        finally:
            self.stop()

    def stop(self) -> None:
        """停止自动对战"""
        self.running = False
        stats = BattleManager().get_stats()
        logger.info(f"最终统计: {stats}")
        logger.info("自动对战已停止")

    def restart_game(self) -> None:
        """重启游戏"""
        logger.info("重启游戏...")
        self.device.stop_app()
        time.sleep(2)
        self.device.start_app()
        time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="皇室战争自动对战")
    parser.add_argument("-d", "--device", default="emulator-5554", help="设备ID")
    parser.add_argument("-w", "--window", default="雷电模拟器", help="窗口名称")
    parser.add_argument("-m", "--max", type=int, default=10, help="最大战斗场次")
    parser.add_argument("-mode", "--mode", default="1v1", choices=["1v1", "2v2"], help="战斗模式")
    parser.add_argument("-s", "--strategy", default="aggressive",
                       choices=["aggressive", "defensive", "random"],
                       help="出牌策略")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel("DEBUG")

    auto = ClashRoyaleAuto(args.device, args.window)
    auto.start(args.max, args.mode, args.strategy)


if __name__ == "__main__":
    main()
