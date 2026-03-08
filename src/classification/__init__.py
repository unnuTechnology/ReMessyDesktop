from pathlib import Path
from src.classification.results import ClassificationResult
from src.classification import cses, regex, scorer, file_type, classisland
from src.classification.registerer import (
    Classifier,
    classifiers,
    register_classifier,
)
from src.util.config import Config


def sorted_classifiers(config: Config) -> list[Classifier]:
    """根据配置返回分类器列表，按优先级排序"""
    return list(
        sorted(
            classifiers,
            key=lambda x: config.classification.priority[x.id],
        )
    )


def classify(path: Path, config: Config) -> str | ClassificationResult:
    """根据路径和配置返回分类结果"""
    for clsr in sorted_classifiers(config):
        match (res := clsr(path, config)):
            case ClassificationResult.UNKNOWN:
                continue
            case ClassificationResult.DELETE:
                return res
            case ClassificationResult.SKIP:
                return ClassificationResult.SKIP
            case _:
                return res
    return ClassificationResult.UNKNOWN


__all__ = (  # pyright: ignore [reportUnsupportedDunderAll]
    ClassificationResult,
    cses,
    classisland,
    regex,
    scorer,
    file_type,
    Classifier,
    classifiers,
    register_classifier,
)
