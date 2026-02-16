from pathlib import Path
import re

from src.classification import registerer
from src.util.config import Config


@registerer.register_classifier("正则表达式分类")
def regex(path: Path, config: Config) -> str | None:
    raise NotImplementedError
