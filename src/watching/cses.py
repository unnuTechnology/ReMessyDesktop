import threading
import time
import datetime

from cses import CSES
from cses.errors import CSESError
from dateutil.parser import parse

from src.watching import Watcher
from src.util.config import Config
from src.util.log import log


class CSESWatcher(Watcher):
    default_name = 'CSES 课表监听器'

    def __init__(self, config: Config):
        super().__init__(config)

        self.thread = threading.Thread(target=self.executor, args=())
        self.running = False

        self.schedule = CSES.from_file(self.config.watching.cses_watcher.cses_path)

        log.debug(f'成功初始化 CSES 课表监听器 ({self})')

    def start_watching(self):
        self.running = True
        if not self.thread.is_alive() and not self.running:
            self.thread = threading.Thread(target=self.executor, args=())
            self.thread.start()
            log.info(f'成功启动 CSES 课表监听器 ({self.thread} @ {self})')
        else:
            log.warning(f'CSES 课表监听器 ({self}) 已被启动过')

    def stop_watching(self):
        self.running = False
        log.info(f'成功停止 CSES 课表监听器 ({self})')

    def executor(self):
        while self.running:
            self.execute()  # 执行所有注册的命令
            if not self.running:
                return
            time.sleep(self.get_next_watch_duration())

    def get_next_watch_duration(self, now_tm: datetime.datetime | None = None) -> int:
        """获取下一次监听的时间间隔（秒）"""
        if now_tm is None:
            now_tm = datetime.datetime.now()
        now = now_tm.time()

        try:
            today_classes = self.schedule.today_schedule(
                start_day=parse(
                    self.config.watching.cses_watcher.start_day, yearfirst=True
                ).date(),
                day=now_tm.date(),
            ).classes
        except CSESError as e:
            log.error(f'CSES 课表本日没有课（{e}）')
            raise AttributeError(f'本日没有课：{e}')

        lesson_times = [
            (
                datetime.datetime.combine(now_tm.date(), lesson.start_time),
                datetime.datetime.combine(now_tm.date(), lesson.end_time),
            )
            for lesson in today_classes
        ]
        try:
            for i, (begin, end) in enumerate(lesson_times):
                if begin < now_tm < end:
                    # 当前时间在上课
                    delta = end - now_tm
                    log.debug(
                        f'当前时间 ({now}) 在课程 "{today_classes[i].subject}" ({begin} - {end}) 上，剩余 {delta}'
                    )
                    return delta.days * 24 * 60 * 60 + delta.seconds  # 转换为总秒数
                elif end < now_tm < lesson_times[i + 1][0]:
                    # 当前时间在下课，计算到下节课下课的时间差
                    delta = lesson_times[i + 1][1] - now_tm
                    log.debug(
                        f'当前时间 ({now}) 在课间，到下节课 "{today_classes[i+1].subject}" ({lesson_times[i+1][0]} - {lesson_times[i+1][1]}) 下课剩余 {delta}'
                    )
                    return delta.days * 24 * 60 * 60 + delta.seconds  # 转换为总秒数
            else:
                raise ValueError(f"当前时间 ({now}) 可能已放学")
        except IndexError as e:
            raise ValueError(f"当前时间 ({now}) 可能已放学") from e

    def __repr__(self):
        return f'<{self.__class__.__name__} schedule={self.schedule} running={self.running}>'
