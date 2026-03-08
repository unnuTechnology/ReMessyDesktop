"""为分类器提供统一的注册服务，同时暴露所有已注册的分类器。"""
from pathlib import Path
from typing import Callable, NamedTuple

from src.classification import ClassificationResult
from src.util.config import Config

# 分类器函数的类型，接受待分类文件路径和配置对象，返回科目名称字符串 (若不需要存放，返回 None)
ClassifierFunc = Callable[[Path, Config], str | ClassificationResult]


class Classifier(NamedTuple):
    """分类器，用于存储已注册的分类器。"""

    name: str  # 分类器人类可读名称
    id: str  # 分类器唯一标识符
    func: ClassifierFunc  # 分类器函数

    def __call__(self, path: Path, config: Config) -> str | ClassificationResult:
        return self.func(path, config)


classifiers: list[Classifier] = []


def register_classifier(
    name: str,
) -> Callable[[ClassifierFunc], ClassifierFunc]:
    """注册一个分类器。"""

    def decorator(func: ClassifierFunc) -> ClassifierFunc:
        classifiers.append(
            Classifier(
                name=name,
                id=getattr(func, '__name__', f'UNKNOWN_classifier_{len(classifiers)}'),
                func=func,
            )
        )
        return func

    return decorator
