from pathlib import Path

from src.classification import registerer, ClassificationResult
from src.util.config import Config


@registerer.register_classifier("文件名(不)智能分类")
def scorer(path: Path, config: Config) -> str | ClassificationResult:
    raise NotImplementedError
