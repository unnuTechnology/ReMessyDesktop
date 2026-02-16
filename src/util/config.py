import os
import pathlib
import json
from typing import Any, Self

import pydantic

from src.util.log import log


DEFAULT_CONFIG_PATH = pathlib.Path.cwd() / "config" / "config.json"
CONFIG_API_VERSION = 1
CONFIG_TEMPLATE = {
    "api_version": CONFIG_API_VERSION,
    "app": {
        "detect_path": str(pathlib.Path.expanduser(pathlib.Path("~/Desktop"))),
    },
}


class _AppConfig(pydantic.BaseModel):
    detect_path: str

    @pydantic.field_validator("detect_path")
    @classmethod
    def validate_path(cls, value: Any) -> bool:
        try:
            path = pathlib.Path(value)
        except ValueError as e:
            log.error(f"配置文件中指定的检测路径 ({value}) 不是一个有效的路径。")
            raise ValueError(f"配置文件中指定的检测路径 ({value}) 不是一个有效的路径。", ) from e
        else:
            if not path.exists():
                log.error(f"配置文件中指定的检测路径 ({value}) 不存在。")
                raise FileNotFoundError(f"配置文件中指定的检测路径 ({value}) 不存在。")
            return value


class Config(pydantic.BaseModel):
    api_version: int
    app: _AppConfig

    @pydantic.field_validator("api_version")
    @classmethod
    def validate_api_version(cls, value: Any) -> bool:
        try:
            ver = int(value)
        except ValueError:
            log.error(f"配置文件中指定的API版本 ({value}) 不是一个有效的整数。")
            return False
        else:
            if ver != CONFIG_API_VERSION:
                log.error(f"配置文件的API版本 ({ver}) 与当前版本 ({CONFIG_API_VERSION}) 不匹配。")
                return False
            return True


def get_config(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> Config:
    """获取配置对象。若不存在，会用模板初始化一个配置文件。"""
    try:
        return build_config(read_config_from(path))
    except FileNotFoundError:
        log.warning(f"配置文件 {path.absolute()!r} 不存在。正在初始化配置。")
        os.makedirs(path.parent, exist_ok=True)
        with path.open("w", encoding="utf8") as f:
            json.dump(CONFIG_TEMPLATE, f, ensure_ascii=False, indent=4)
        return build_config(CONFIG_TEMPLATE)


def is_valid_config(config: dict) -> bool:
    """检查 ``config`` 是否是一个有效的配置字典。"""
    try:
        build_config(config)
    except (pydantic.ValidationError, ValueError) as e:
        log.error(f"配置文件 {config} 不是一个有效的配置字典：{e}")
        return False
    return True


def build_config(config: dict) -> Config:
    """从 ``config`` 构建一个 ``Config`` 对象。"""
    built = Config(**config)
    log.debug(f"成功构建配置对象：{built!r}")
    return built


def read_config_from(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> dict:
    """从 ``path`` 读取配置文件（若读取失败则返回空字典）。不考虑读取的文件内容是否是有效的配置文件。"""
    try:
        with path.open("r", encoding="utf8") as f:
            config = json.load(f)
            log.info(f"成功从 {path.absolute()!r} 读取配置文件。")
            return config
    except FileNotFoundError:
        log.error(f"配置文件 {path.absolute()!r} 不存在。")
        raise
    except json.JSONDecodeError:
        log.error(f"配置文件 {path.absolute()!r} 的JSON格式错误。")
        raise
