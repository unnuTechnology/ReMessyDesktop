import datetime
from pathlib import Path

from cses import CSES
from cses.errors import CSESError
from dateutil.parser import parse

from src.classification import registerer, ClassificationResult
from src.util.config import Config
from src.util.log import log


@registerer.register_classifier("CSES 课表分类")
def cses_classifier(_: Path, config: Config, now_tm: datetime.datetime | None = None) -> str | ClassificationResult:
    log.debug(f'正在从 CSES 课表 ({config.classification.cses_classifier.cses_path}) 中获取今日课程')
    if now_tm is None:
        now_tm = datetime.datetime.now()
    now = now_tm.time()

    schedule = CSES.from_file(config.classification.cses_classifier.cses_path)
    try:
        today_classes = schedule.today_schedule(
            start_day=parse(config.classification.cses_classifier.start_day, yearfirst=True).date(),
            day=now_tm.date()
        ).classes
    except CSESError as e:
        # 本日没有课
        log.debug(f'本日 ({now_tm.date()}) 没有课，返回 UNKNOWN ({e})')
        return ClassificationResult.UNKNOWN

    times_subject = [
        ((lesson.start_time, lesson.end_time), lesson.subject) for lesson in today_classes
    ]
    for i, ((start, end), subject) in enumerate(times_subject):
        try:
            if start <= now <= end:  # 上课时
                log.debug(f'当前时间 ({now}) 在 {subject}({start}-{end}) 之间，返回课程 ({subject})')
                return subject
            if end <= now < times_subject[i+1][0][0]:  # 上节课下课，下一个课程开始之前（下课）
                log.debug(f'当前时间 ({now}) 在 课间({end}-{times_subject[i+1][0][0]}) 之间，返回课程 ({subject})')
                return subject  # （算作上节课）
        except IndexError:
            # 最后一节课，times_subject[i+1][0][0] 抛出异常
            # 此时第一个 if 语句完成判断（并且没有执行），则说明当前时间在最后一节课之后
            log.debug(f'当前时间 ({now}) 在 放学后({end}-) 之间，返回 UNKNOWN')
            return subject
    else:
        log.debug('没有匹配项，返回 UNKNOWN')
        return ClassificationResult.UNKNOWN
