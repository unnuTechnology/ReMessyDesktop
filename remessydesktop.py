from src.util.log import log
from src.util.versioning import VERSION_FULL
from src.util import config


class ReMessyDesktop:
    def __init__(self):
        log.info("ReMessyDesktop 正在初始化……")
        self.config = config.get_config()
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
