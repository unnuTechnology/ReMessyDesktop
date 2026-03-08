from src.watching import Watcher


class ClassIslandWatcher(Watcher):
    default_name = 'ClassIsland 监听器'

    def start_watching(self):
        raise NotImplementedError

    def stop_watching(self):
        raise NotImplementedError
