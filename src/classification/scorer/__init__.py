from collections import Counter
from pathlib import Path
import json

from jieba import cut

from src.classification import registerer, ClassificationResult
from src.util.config import Config
from src.util.log import log


@registerer.register_classifier("文件名(不)智能分类")
def scorer_classifier(path: Path, config: Config) -> str | ClassificationResult:
    filename = path.name.removesuffix(path.suffix)  # 去除扩展名
    split = list(cut(filename))

    scores = Counter()
    log.debug(f"正在为 {filename!r} (分词后{split!r}) 执行 scorer 分类")
    with open("src/classification/scorer/data.json", "r", encoding="utf-8") as f:
        scoring_data = json.load(f)
    for subject, keywords in scoring_data.items():
        scores[subject] = sum(1 for keyword in keywords if keyword in split)

    top3 = scores.most_common(3)
    top3_scores = list(sorted(dict(top3).values(), reverse=True))
    log.debug(f"为 {filename!r} 分类得到的分数：{scores!r}，前三大为 {top3!r}，前三大分数为 {top3_scores!r}")

    if top3_scores:
        return top3[0][0]
    else:
        return ClassificationResult.UNKNOWN
