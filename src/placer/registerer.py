"""为放置器提供统一的注册服务，同时暴露所有已注册的放置器。"""
from typing import Callable, NamedTuple
from pathlib import Path

from src.classification import ClassificationResult
from src.util.config import Config
from src.util.log import log

# 放置器函数的类型，接受分类结果或科目名称字符串、配置与待放置文件路径，并进行相应的文件操作
PlacerFunc = Callable[[str | ClassificationResult, Config, Path], None]


class Placer(NamedTuple):
    """放置器，用于存储已注册的放置器。"""

    name: str  # 放置器人类可读名称
    id: str  # 放置器唯一标识符
    func: PlacerFunc  # 放置器函数

    def __call__(
        self, result: str | ClassificationResult, config: Config, path: Path
    ) -> None:
        return self.func(result, config, path)


placers: list[Placer] = []


def register_placer(name: str) -> Callable[[PlacerFunc], PlacerFunc]:
    """注册一个放置器。"""

    def decorator(func: PlacerFunc) -> PlacerFunc:
        placers.append(
            Placer(
                name=name,
                id=getattr(func, '__name__', f'UNKNOWN_placer_{len(placers)}'),
                func=func,
            )
        )
        log.debug(f'放置器 {placers[-1]} 成功注册。')
        return func

    return decorator
