from enum import Enum


class ClassificationResult(Enum):
    DELETE = 'DELETE'  # 删除文件
    SKIP = 'SKIP'  # 不处理此文件
    UNKNOWN = 'UNKNOWN'  # 此分类器不能处理此文件，应尝试下一个分类器
