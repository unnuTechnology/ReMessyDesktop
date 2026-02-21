import pathlib

from src.classification import regex
from src.classification.results import ClassificationResult
from src.util import config


example_config = config.Config(**config.CONFIG_TEMPLATE)
example_config.classification.regex_classifier = config._RegexClassifierConfig(
    patterns={
        "S1": r"^S1-.*$",
        "S2": r"^.*-S2$",
    }
)


def test_regex_classifier():
    assert regex.regex_classifier(pathlib.Path("./S1-abc.pptx"), example_config) == "S1"
    assert regex.regex_classifier(pathlib.Path("./abc-S2.pptx"), example_config) == "S2"


def test_classifier_skip():
    assert regex.regex_classifier(pathlib.Path("./foobar.docx"), example_config) == ClassificationResult.SKIP
