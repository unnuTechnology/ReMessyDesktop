"""为分类器提供统一的注册服务，同时暴露所有已注册的分类器。"""
from pathlib import Path
from typing import Callable, NamedTuple

from src.classification import ClassificationResult
from src.util.config import Config
from src.util.log import log

# 分类器函数的类型，接受待分类文件路径和配置对象，返回科目名称字符串 (若不需要存放，返回 None)
ClassifierFunc = Callable[[Path, Config], str | ClassificationResult]


class ClassifierDict(NamedTuple):
    """分类器，用于存储已注册的分类器。"""
    name: str  # 分类器人类可读名称
    id: str  # 分类器唯一标识符
    func: ClassifierFunc  # 分类器函数


classifiers: list[ClassifierDict] = []


def register_classifier(name: str) -> Callable[[ClassifierFunc], ClassifierFunc]:
    """注册一个分类器。"""
    def decorator(func: ClassifierFunc) -> ClassifierFunc:
        classifiers.append(ClassifierDict(name=name, id=func.__name__, func=func))
        log.debug(f"分类器 {name} ({func.__name__}) 成功注册。")
        return func
    return decorator
