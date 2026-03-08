import threading
import time

from src.watching import Watcher
from src.util.config import Config


class CSESWatcher(Watcher):
    default_name = 'CSES 课表监听器'

    def __init__(self, config: Config):
        super().__init__(config)
        self.thread = threading.Thread(target=self.executor, args=())
        self.running = False

    def start_watching(self):
        self.running = True
        self.thread.start()

    def stop_watching(self):
        self.running = False

    def executor(self):
        while self.running:
            self.execute()  # 执行所有注册的命令
            time.sleep(self.get_next_watch_duration())

    def get_next_watch_duration(self) -> int:
        """获取下一次监听的时间间隔（秒）"""
        return 1
