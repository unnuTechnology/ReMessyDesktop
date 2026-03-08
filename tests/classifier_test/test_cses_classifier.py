from datetime import datetime
from pathlib import Path

import pytest

from src.classification.results import ClassificationResult
from src.classification import cses
from src.util import config


example_config = config.Config(**config.CONFIG_TEMPLATE)  # ty: ignore
example_config.classification.cses_classifier = config._CSESClassifierConfig(
    cses_path='./tests/classifier_test/cses_example.yaml',
    start_day='2026/03/02',
)


@pytest.mark.parametrize(
    'now, expected',
    [
        (
            datetime(2026, 3, 2, 7, 30, 0),
            ClassificationResult.UNKNOWN,
        ),  # 所有课开始前
        (datetime(2026, 3, 2, 8, 30, 0), '数学'),  # 通用，课中
        (datetime(2026, 3, 3, 8, 30, 0), '物理'),  # 单周，课中
        (datetime(2026, 3, 3, 9, 5, 0), '物理'),  # 单周，下课
        (datetime(2026, 3, 3, 9, 30, 0), '英语'),  # 单周，最后一节课
        (datetime(2026, 3, 10, 9, 30, 0), '英语'),  # 双周，课中
        (
            datetime(2026, 3, 3, 10, 30, 0),
            ClassificationResult.UNKNOWN,
        ),  # 单周，放学后
        (
            datetime(2026, 3, 4, 8, 30, 0),
            ClassificationResult.UNKNOWN,
        ),  # 找不到课表
    ],
)
def test_cses_classifier(now, expected):
    result = cses.cses_classifier(
        Path(''),
        example_config,
        now_tm=now,  # ty: ignore  # pyright: ignore
    )
    assert result == expected
