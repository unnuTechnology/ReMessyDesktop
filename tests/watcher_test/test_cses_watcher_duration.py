from datetime import datetime

import pytest

from src.watching.cses import CSESWatcher
from src.util import config


example_config = config.Config(**config.CONFIG_TEMPLATE)  # ty: ignore
example_config.watching.cses_watcher = config._CSESWatcherConfig(
    cses_path="./tests/cses_example.yaml",
    start_day="2026/03/02",
)


@pytest.mark.parametrize(
    "now, excepted",
    [
        (datetime(2026, 3, 2, 8, 30), 30 * 60),  # 课中
        (datetime(2026, 3, 17, 9, 5), (5+60) * 60),  # 课后
    ],
)
def test_cses_watcher_duration(now, excepted):
    cs = CSESWatcher(example_config)
    assert cs.get_next_watch_duration(now) == excepted


def test_cses_watcher_duration_no_lesson_error():
    cs = CSESWatcher(example_config)
    with pytest.raises(AttributeError):
        cs.get_next_watch_duration(datetime(2026, 3, 7, 8, 30))


def test_cses_watcher_duration_lesson_end_error():
    cs = CSESWatcher(example_config)
    with pytest.raises(ValueError):
        cs.get_next_watch_duration(datetime(2026, 3, 2, 12, 0))
