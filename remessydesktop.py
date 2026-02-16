from src.util.log import log
from src.util.versioning import VERSION_FULL
from src.util import config
from src.classification import classifiers


class ReMessyDesktop:
    def __init__(self):
        log.info("ReMessyDesktop 正在初始化……")
        self.config = config.get_config()
        log.debug(f"获取到的分类器：{classifiers!r}")
        log.success(f"ReMessyDesktop ({VERSION_FULL}) 成功初始化。")

    def run(self):
        log.success("ReMessyDesktop 开始运行。")


if __name__ == "__main__":
    try:
        app = ReMessyDesktop()
        app.run()
    except Exception as e:
        log.critical(f"发生不可恢复的错误：{e}")
        exit(1)
