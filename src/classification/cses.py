from pathlib import Path


from src.classification import registerer, ClassificationResult
from src.util.config import Config


@registerer.register_classifier("CSES 课表分类")
def cses_schedule(path: Path, config: Config) -> str | ClassificationResult:
    return ClassificationResult.SKIP
