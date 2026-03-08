from pathlib import Path

from src.classification import registerer, ClassificationResult
from src.util.config import Config


@registerer.register_classifier('文件类型分类')
def file_type_classifier(
    path: Path, config: Config
) -> str | ClassificationResult:
    ft = path.suffix.removeprefix('.')  # 去除扩展名的前导点
    for (
        type_,
        subject,
    ) in config.classification.file_type_classifier.rules.items():
        if type_ == ft:
            if subject == 'SKIP':
                return ClassificationResult.SKIP
            elif subject == 'DELETE':
                return ClassificationResult.DELETE
            else:
                return subject
    else:
        return ClassificationResult.UNKNOWN
