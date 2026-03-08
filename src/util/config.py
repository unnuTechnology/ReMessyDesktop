import os
import pathlib
import json
from typing import Any

import pydantic

from src.util.log import log

DEFAULT_CONFIG_PATH = pathlib.Path.cwd() / 'config' / 'config.json'
CONFIG_API_VERSION = 1
CONFIG_TEMPLATE = {
    'api_version': CONFIG_API_VERSION,
    'app': {
        'detect_path': str(pathlib.Path.expanduser(pathlib.Path('~/Desktop'))),
    },
    'classification': {
        'cses_classifier': {'cses_path': '', 'start_day': '1970-01-01'},
        'regex_classifier': {'patterns': {}},
        'file_type_classifier': {'rules': {}},
        'priority': {
            'cses_classifier': 1,
            'regex_classifier': 0,
            'scorer_classifier': 2,
            'file_type_classifier': 3,
        },
    },
    'placing': {
        'enabled_placer': 'default_placer',
        'default_placer': {'places': {}},
    },
}


class _CSESClassifierConfig(pydantic.BaseModel):
    cses_path: str
    start_day: str


class _RegexClassifierConfig(pydantic.BaseModel):
    patterns: dict[str, str]


class _FileTypeClassifierConfig(pydantic.BaseModel):
    rules: dict[str, str]


class _ClassificationConfig(pydantic.BaseModel):
    cses_classifier: _CSESClassifierConfig
    regex_classifier: _RegexClassifierConfig
    file_type_classifier: _FileTypeClassifierConfig
    priority: dict[str, int]

    @pydantic.field_validator('priority')
    @classmethod
    def validate_priority(cls, value: dict[str, int]) -> dict[str, int]:
        for key in [
            'cses_classifier',
            'regex_classifier',
            'scorer_classifier',
            'file_type_classifier',
        ]:
            if key not in value:
                log.error(f'配置文件中缺少分类器优先级项 {key}。')
                raise KeyError(f'配置文件中缺少分类器优先级项 {key}。')

        sorted_values = sorted(tuple(value.values()))
        if any(i != j for i, j in enumerate(sorted_values)):
            log.error(f'配置文件中分类器优先级项 ({value}) 的值必须从 0 开始并且连续。')
            raise ValueError(f'配置文件中分类器优先级项 ({value}) 的值必须从 0 开始并且连续。')

        return value


class _DefaultPlacerConfig(pydantic.BaseModel):
    places: dict[str, str]


class _PlacingConfig(pydantic.BaseModel):
    enabled_placer: str
    default_placer: _DefaultPlacerConfig


class _AppConfig(pydantic.BaseModel):
    detect_path: str

    @pydantic.field_validator('detect_path')
    @classmethod
    def validate_path(cls, value: Any) -> bool:
        try:
            path = pathlib.Path(value)
        except ValueError as e:
            log.error(f'配置文件中指定的检测路径 ({value}) 不是一个有效的路径。')
            raise ValueError(
                f'配置文件中指定的检测路径 ({value}) 不是一个有效的路径。',
            ) from e
        else:
            if not path.exists():
                log.error(f'配置文件中指定的检测路径 ({value}) 不存在。')
                raise FileNotFoundError(f'配置文件中指定的检测路径 ({value}) 不存在。')
            return value


class Config(pydantic.BaseModel):
    api_version: int
    app: _AppConfig
    classification: _ClassificationConfig
    placing: _PlacingConfig

    @pydantic.field_validator('api_version')
    @classmethod
    def validate_api_version(cls, value: Any) -> bool:
        try:
            ver = int(value)
        except ValueError:
            log.error(f'配置文件中指定的API版本 ({value}) 不是一个有效的整数。')
            return False
        else:
            if ver != CONFIG_API_VERSION:
                log.error(
                    f'配置文件的API版本 ({ver}) 与当前版本 ({CONFIG_API_VERSION}) 不匹配。'
                )
                return False
            return True


def get_config(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> Config:
    """获取配置对象。若不存在，会用模板初始化一个配置文件。"""
    try:
        return build_config(read_config_from(path))
    except FileNotFoundError:
        log.warning(f'配置文件 {path.absolute()!r} 不存在。正在初始化配置。')
        os.makedirs(path.parent, exist_ok=True)
        with path.open('w', encoding='utf8') as f:
            json.dump(CONFIG_TEMPLATE, f, ensure_ascii=False, indent=4)
        return build_config(CONFIG_TEMPLATE)


def is_valid_config(config: dict) -> bool:
    """检查 ``config`` 是否是一个有效的配置字典。"""
    try:
        build_config(config)
    except (pydantic.ValidationError, ValueError) as e:
        log.error(f'配置文件 {config} 不是一个有效的配置字典：{e}')
        return False
    return True


def build_config(config: dict) -> Config:
    """从 ``config`` 构建一个 ``Config`` 对象。"""
    built = Config(**config)
    log.debug(f'成功构建配置对象：{built!r}')
    return built


def read_config_from(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> dict:
    """从 ``path`` 读取配置文件（若读取失败则返回空字典）。不考虑读取的文件内容是否是有效的配置文件。"""
    try:
        with path.open('r', encoding='utf8') as f:
            config = json.load(f)
            log.info(f'成功从 {path.absolute()!r} 读取配置文件。')
            return config
    except FileNotFoundError:
        log.error(f'配置文件 {path.absolute()!r} 不存在。')
        raise
    except json.JSONDecodeError:
        log.error(f'配置文件 {path.absolute()!r} 的JSON格式错误。')
        raise
