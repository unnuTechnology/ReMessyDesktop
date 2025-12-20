from src.log_util import log


class RemessyDesktop:
    def __init__(self):
        log.warning(f"RemessyDesktop ({VERSION}) 成功初始化。")

    def run(self):
        log.warning("RemessyDesktop 开始运行。")


if __name__ == "__main__":
    app = RemessyDesktop()
    app.run()
