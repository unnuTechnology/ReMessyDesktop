from src.util.log import log
from src.util.versioning import VERSION_FULL


class ReMessyDesktop:
    def __init__(self):
        log.success(f"ReMessyDesktop ({VERSION_FULL}) 成功初始化。")

    def run(self):
        log.success("ReMessyDesktop 开始运行。")


if __name__ == "__main__":
    app = ReMessyDesktop()
    app.run()
