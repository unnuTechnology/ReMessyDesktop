import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s %(name)s] %(levelname)s | %(message)s",
    encoding="utf-8",
)
log = logging.getLogger(__name__)


class RemessyDesktop:
    def __init__(self):
        log.warning("RemessyDesktop initialized.")

    def run(self):
        log.warning("RemessyDesktop is running.")


if __name__ == "__main__":
    app = RemessyDesktop()
    app.run()
