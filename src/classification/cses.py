from pathlib import Path

import cses

from src.classification import registerer
from src.util.config import Config


@registerer.register_classifier("CSES 课表分类")
def cses(path: Path, config: Config) -> str | None:
    raise NotImplementedError
