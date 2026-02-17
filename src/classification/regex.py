from pathlib import Path
import re

from src.classification import registerer, ClassificationResult
from src.util.config import Config


@registerer.register_classifier("正则表达式分类")
def regex_classifier(path: Path, config: Config) -> str | ClassificationResult:
    filename = "".join(path.name.split(".")[:-1])  # 去除扩展名
    patterns = {
        subject: re.compile(pattern)
        for subject, pattern in
        config.classification.regex_classifier.patterns.items()
    }
    for subject, pattern in patterns.items():
        if pattern.match(filename):
            return subject
    else:
        return ClassificationResult.SKIP
