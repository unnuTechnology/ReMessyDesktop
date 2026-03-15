import time
import traceback

from src.util.log import log
from src.util.versioning import VERSION_FULL, BUILD_CODE
from src.util import config
from src.classification import classifiers
from src.placer import placers
from src.watching import watchers


class ReMessyDesktop:
    def __init__(self):
        log.info(f'ReMessyDesktop ({BUILD_CODE}) 正在初始化……')
        self.config = config.get_config()
        log.add(
            "./logs/RMD-LOG-{time}.log",
            level=self.config.app.log_level,
            retention="1 week",
        )
        log.debug(f'获取到的分类器：{classifiers!r}')
        log.debug(f'获取到的存放器：{placers!r}')
        log.debug(f'获取到的监听器：{watchers!r}')
        log.success(f'ReMessyDesktop ({VERSION_FULL}) 成功初始化。')

    def run(self):
        log.debug('正在启动监听器绑定……')
        for watcher in watchers:
            try:
                this_watcher = watcher(self.config)
                this_watcher.add_command(self.on_check)
                this_watcher.start_watching()
            except Exception as e:
                log.warning(f'监听器 {watcher} 启动失败：{type(e).__name__}: {e}')
        log.success('ReMessyDesktop 开始运行。')
        while True:
            time.sleep(0)  # Take a break

    def on_check(self):
        log.info('触发了分类!')


if __name__ == '__main__':
    try:
        app = ReMessyDesktop()
        app.run()
    except BaseException as e:
        log.critical(f'发生不可恢复的错误：{type(e).__name__}: {e}')
        log.critical(traceback.format_exc())
        exit(-1)
