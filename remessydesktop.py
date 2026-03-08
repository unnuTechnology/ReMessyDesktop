import traceback

from src.util.log import log
from src.util.versioning import VERSION_FULL, BUILD_CODE
from src.util import config
from src.classification import classifiers
from src.placer import placers


class ReMessyDesktop:
    def __init__(self):
        log.info(f'ReMessyDesktop ({BUILD_CODE}) 正在初始化……')
        self.config = config.get_config()
        log.debug(f'获取到的分类器：{classifiers!r}')
        log.debug(f'获取到的存放器：{placers!r}')
        log.success(f'ReMessyDesktop ({VERSION_FULL}) 成功初始化。')

    def run(self):
        log.success('ReMessyDesktop 开始运行。')


if __name__ == '__main__':
    try:
        app = ReMessyDesktop()
        app.run()
    except Exception as e:
        log.critical(f'发生不可恢复的错误：{type(e).__name__}: {e}')
        log.debug(traceback.format_exc())
        exit(1)
