from abc import ABC, abstractmethod
from enum import Enum
import time


class TaskStatus(Enum):
    """任务状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseTask(ABC):
    """任务基类"""

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.status = TaskStatus.IDLE
        self.error_count = 0
        self.max_errors = 3
        self.start_time: float = 0
        self.end_time: float = 0

    @abstractmethod
    def execute(self) -> bool:
        """执行任务，返回是否成功"""
        pass

    def check_preconditions(self) -> bool:
        """检查前置条件"""
        return True

    def on_start(self) -> None:
        """任务开始回调"""
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        self.on_status_change("RUNNING")

    def on_complete(self, success: bool = True) -> None:
        """任务完成回调"""
        self.end_time = time.time()
        self.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        duration = self.end_time - self.start_time
        self.on_status_change(f"{self.status.value} (耗时: {int(duration)}s)")

    def on_error(self, error: Exception) -> None:
        """错误处理回调"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.on_complete(success=False)

    def on_status_change(self, status: str) -> None:
        """状态变化回调"""
        import logging
        logger = logging.getLogger(self.__class__.__name__)
        logger.info(f"[{self.name}] {status}")

    def run(self) -> TaskStatus:
        """运行任务"""
        if not self.check_preconditions():
            self.on_complete(success=False)
            return self.status

        self.on_start()

        try:
            result = self.execute()
            self.on_complete(success=result)
        except Exception as e:
            self.on_error(e)
            raise

        return self.status

    def reset(self) -> None:
        """重置任务状态"""
        self.status = TaskStatus.IDLE
        self.error_count = 0
        self.start_time = 0
        self.end_time = 0
