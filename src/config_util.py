import os
import pathlib
import json

from src.log_util import log


DEFAULT_CONFIG_PATH = pathlib.Path.cwd() / "config" / "config.json"
CONFIG_API_VERSION = 1


def is_valid_config(config: dict) -> bool:
    """检查 ``config`` 是否是一个有效的配置字典。"""
    api_version = config.get("api-version", 0)
    if api_version != CONFIG_API_VERSION:
        log.error(f"配置文件的API版本 ({api_version}) 与当前版本 ({CONFIG_API_VERSION}) 不匹配。")
        return False
    if "app" not in config.keys():
        log.error("配置文件中缺少 'app' 键。")
        return False
    if "detect_path" not in config["app"].keys():
        log.error("配置文件中缺少 'app.detect_path' 键。")
        return False
    if not pathlib.Path(config["app"]["detect_path"]).exists():
        log.error(f"配置文件中指定的检测路径 ({config['app']['detect_path']}) 不存在。")
        return False
    return True


def read_config_from(path: pathlib.Path = DEFAULT_CONFIG_PATH) -> dict:
    """从 ``path`` 读取配置文件（若读取失败则返回空字典）。不考虑读取的文件内容是否是有效的配置文件。"""
    try:
        with path.open("r", encoding="utf8") as f:
            config = json.load(f)
            log.info(f"成功从 {path.absolute()!r} 读取配置文件。")
            return config
    except FileNotFoundError:
        log.error(f"配置文件 {path.absolute()!r} 不存在。")
        return {}
    except json.JSONDecodeError:
        log.error(f"配置文件 {path.absolute()!r} 的JSON格式错误。")
        return {}
