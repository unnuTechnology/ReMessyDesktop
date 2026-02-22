from typing import Iterable
import pytest

from src.util.config import _ClassificationConfig

validator = _ClassificationConfig.validate_priority


def get_priority(priority: Iterable[int]) -> dict[str, int]:
    return {k: v for k, v in zip(
        [
            "cses_classifier",
            "regex_classifier",
            "scorer_classifier",
            "file_type_classifier"
        ],
        priority, strict=True)}


def test_validator_ok() -> None:
    assert validator(get_priority(range(4))) == get_priority(range(4))


def test_not_start_from_zero() -> None:
    with pytest.raises(ValueError):
        validator(get_priority(range(1, 5)))


def test_not_continual() -> None:
    with pytest.raises(ValueError):
        validator(get_priority([0, 2, 3, 4]))


def test_duplicate() -> None:
    with pytest.raises(ValueError):
        validator(get_priority([0, 0, 1, 2]))
