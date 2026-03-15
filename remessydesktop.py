import os
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
        self.desktop_list = self._get_current_desktop_files()
        log.add(
            './logs/RMD-LOG-{time}.log',
            level=self.config.app.log_level,
            retention='1 week',
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
        """
        当一个 Watcher 触发检测时调用的方法。
        """
        log.info('触发了分类!')
        new_files = self._new_files()
        log.debug(f'新增的文件：{new_files}')

    def _get_current_desktop_files(self):
        """
        获取当前桌面文件夹中的所有文件（不包括文件夹）。
        """
        return [
            f
            for f in os.listdir(self.config.app.detect_path)
            if not os.path.isdir(os.path.join(self.config.app.detect_path, f))
        ]

    def _new_files(self):
        """
        比较现在桌面和前一次更新 ``self.desktop_list`` 时的文件列表，返回新增的文件，更新 ``self.desktop_list``。
        """
        current_files = self._get_current_desktop_files()
        new_files = list(set(current_files) - set(self.desktop_list))

        self.desktop_list = current_files
        return new_files


if __name__ == '__main__':
    try:
        app = ReMessyDesktop()
        app.run()
    except BaseException as e:
        log.critical(f'发生不可恢复的错误：{type(e).__name__}: {e}')
        log.critical(traceback.format_exc())
        exit(-1)
