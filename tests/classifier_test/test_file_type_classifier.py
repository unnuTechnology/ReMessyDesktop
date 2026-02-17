import pathlib

import pytest

from src.classification import file_type
from src.classification.results import ClassificationResult
from src.util import config

example_config = config.Config(
    api_version=1,
    app=config._AppConfig(
        detect_path=".",
    ),
    classification=config._ClassificationConfig(
        cses_classifier=config._CSESClassifierConfig(
            cses_path="",
        ),
        regex_classifier=config._RegexClassifierConfig(
            patterns={}
        ),
        file_type_classifier=config._FileTypeClassifierConfig(
            rules={
                "png": "EN",
                "txt": "CN",
                "tmp": "DELETE",
                "pptx": "SKIP",
            }
        )
    )
)


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
    assert file_type.filetype(path, example_config) == expected
