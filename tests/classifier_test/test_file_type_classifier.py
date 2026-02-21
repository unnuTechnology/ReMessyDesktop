import pathlib

import pytest

from src.classification import file_type
from src.classification.results import ClassificationResult
from src.util import config


example_config = config.Config(**config.CONFIG_TEMPLATE)
example_config.classification.file_type_classifier = config._FileTypeClassifierConfig(rules={
    "png": "EN",
    "txt": "CN",
    "tmp": "DELETE",
    "pptx": "SKIP",
})


@pytest.mark.parametrize(
    "path, expected",
    [
        (pathlib.Path("test.png"), "EN"),
        (pathlib.Path("test.txt"), "CN"),
        (pathlib.Path("test.tmp"), ClassificationResult.DELETE),
        (pathlib.Path("test.pptx"), ClassificationResult.SKIP),
        (pathlib.Path("test"), ClassificationResult.SKIP),
    ]
)
def test_file_type_classifier(path, expected):
    assert file_type.file_type_classifier(path, example_config) == expected
