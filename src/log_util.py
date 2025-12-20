import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s %(name)s] %(levelname)s | %(message)s",
    encoding="utf-8",
)
log = logging.getLogger(__name__)
