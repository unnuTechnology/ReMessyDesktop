import os
from pathlib import Path

from send2trash import send2trash

from src.classification import ClassificationResult
from src.placer import register_placer
from src.util.config import Config


@register_placer('默认放置器')
def default_placer(result: str | ClassificationResult, config: Config, path: Path):
    """默认放置器，根据分类结果与配置将文件放置到对应的科目文件夹中。"""
    places = config.placing.default_placer.places

    if result == ClassificationResult.DELETE:
        send2trash(path)
    elif result in (ClassificationResult.SKIP, ClassificationResult.UNKNOWN):
        return
    else:
        os.rename(path, places[result])
