from src.util.log import log
from src.util.versioning import VERSION_FULL


class RemessyDesktop:
    def __init__(self):
        log.success(f"RemessyDesktop ({VERSION_FULL}) 成功初始化。")

    def run(self):
        log.success("RemessyDesktop 开始运行。")


if __name__ == "__main__":
    app = RemessyDesktop()
    app.run()
