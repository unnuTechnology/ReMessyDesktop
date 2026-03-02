from pathlib import Path
from src.classification import registerer, ClassificationResult
from src.util.config import Config
from src.util import classisland_connect as ci


@registerer.register_classifier("ClassIsland 联动分类")
def classisland_classifier(_1: Path, _2: Config) -> ClassificationResult:
    ci_ipc = ci.CSharpIPCHandler()
    if not ci_ipc.start_ipc_client():
        return ClassificationResult.UNKNOWN
    
    res = ci_ipc.get_current_class_info()
    print(res)
    if not res:
        res = ci_ipc.get_previous_class_info()
        print(res)
        if not res:
            ci_ipc.stop_ipc_client()
            return ClassificationResult.UNKNOWN

    ci_ipc.stop_ipc_client()
    return res["name"] or ClassificationResult.UNKNOWN
