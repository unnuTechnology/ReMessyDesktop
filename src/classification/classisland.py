from pathlib import Path

from src.classification import registerer, ClassificationResult
from src.util.config import Config
from src.util import classisland_connect as ci
from src.util.log import log


@registerer.register_classifier("ClassIsland 联动分类")
def classisland_classifier(_1: Path, _2: Config) -> ClassificationResult:
    try:
        with ci.CSharpIPCHandler() as ci_ipc:
            res = ci_ipc.get_current_class_info()
            log.debug(f"ClassIsland 当前课程信息：{res}")
            if not res:
                log.warning("ClassIsland 当前课程返回空值，尝试获取上节课课程信息")
                res = ci_ipc.get_previous_class_info()
                log.debug(f"ClassIsland 上节课课程信息：{res}")
                if not res:
                    log.warning("ClassIsland 上节课课程返回空值，无法分类")
                    return ClassificationResult.UNKNOWN

            log.success(f"从 ClassIsland 获取课程成功: {res}")
            return res["name"] or ClassificationResult.UNKNOWN
    except ci.IPCError as e:
        log.error(f"ClassIsland IPC 错误：{e}，无法分类")
        return ClassificationResult.UNKNOWN
