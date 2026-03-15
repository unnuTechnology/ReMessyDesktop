from typing import Callable, Any
from abc import ABC, abstractmethod

from src.util.config import Config


WatchReceiver = Callable[[], Any]
watchers: list[type['Watcher']] = []


class Watcher(ABC):
    default_name = ''

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        watchers.append(cls)

    def __init__(self, config: Config, name: str = default_name):
        self.name = name
        self.config = config
        self.funcs: list[WatchReceiver] = []

    @abstractmethod
    def start_watching(self):
        """开始监听"""
        raise NotImplementedError

    @abstractmethod
    def stop_watching(self):
        """停止监听"""
        raise NotImplementedError

    def add_command(self, fn: WatchReceiver) -> None:
        self.funcs.append(fn)

    def execute(self) -> None:
        for fn in self.funcs:
            fn()

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name!r} config={self.config!r} funcs={self.funcs!r}>'
