import pathlib

from src.classification import regex
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
            patterns={
                "S1": r"^S1-.*$",
                "S2": r"^.*-S2$",
            }
        ),
        file_type_classifier=config._FileTypeClassifierConfig(
            rules={}
        )
    )
)


def test_regex_classifier():
    assert regex.regex_classifier(pathlib.Path("./S1-abc.pptx"), example_config) == "S1"
    assert regex.regex_classifier(pathlib.Path("./abc-S2.pptx"), example_config) == "S2"


def test_classifier_skip():
    assert regex.regex_classifier(pathlib.Path("./foobar.docx"), example_config) == ClassificationResult.SKIP
