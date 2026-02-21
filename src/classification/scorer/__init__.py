from collections import Counter
from pathlib import Path
import json

from jieba import cut

from src.classification import registerer, ClassificationResult
from src.util.config import Config


@registerer.register_classifier("文件名(不)智能分类")
def scorer_classifier(path: Path, config: Config) -> str | ClassificationResult:
    filename = path.name.removesuffix(path.suffix)  # 去除扩展名
    split = cut(filename)

    scores = Counter()
    with open("/src/classification/scorer/data.json", "r", encoding="utf-8") as f:
        scoring_data = json.load(f)
    for subject, keywords in scoring_data.items():
        scores[subject] = sum(1 for keyword in keywords if keyword in split)

    top3 = scores.most_common(3)
    top3_scores = list(sorted(dict(top3).values()))
    if len(top3_scores) < 3:
        return ClassificationResult.SKIP  # 匹配太少
    if top3_scores[2] - top3_scores[0] < 3:
        return ClassificationResult.SKIP  # 匹配差异太小

    return top3[0][0]
