import sys
import time
import traceback
import asyncio
import threading
from typing import Optional, Any

from src.util.log import log


class IPCError(RuntimeError):
    """ClassIsland IPC 错误"""


csharp_ok = False

if sys.platform != 'win32':
    log.warning(f"ClassIsland 联动仅在 Windows 上可用， 目前平台： {sys.platform}")
else:
    try:
        sys.path.append("./data/")

        from pythonnet import load

        load(
            "coreclr", runtime_config="data/dotnet.runtimeconfig.json"
        )

        import clr

        clr.AddReference("ClassIsland.Shared.IPC")

        from System import Action, DateTime, Version
        from ClassIsland.Shared.Enums import TimeState
        from ClassIsland.Shared.IPC import IpcClient, IpcRoutedNotifyIds
        from ClassIsland.Shared.IPC.Abstractions.Services import IPublicLessonsService
        from dotnetCampus.Ipc.CompilerServices.GeneratedProxies import (
            GeneratedIpcFactory,
        )
    except Exception as e:
        log.error("无法加载 Python.NET / ClassIsland 联动服务。")
        log.debug(f"{e.__class__.__name__}: {e}")
        log.debug(traceback.format_exc())
        log.warning("CSharpIPCHandler 已被定义为无行为的的类。")
    else:
        log.success("成功加载 Python.NET / ClassIsland 联动服务！")
        csharp_ok = True

if csharp_ok:
    class CSharpIPCHandler:
        """C# dotnetCampus.Ipc 处理器，用于连接 ClassIsland 实例"""

        _instance: Optional["CSharpIPCHandler"] = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

        @classmethod
        def instance(cls):
            """获取单例实例"""
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

        def __init__(self):
            """
            初始化 C# IPC 处理器
            """
            self.ipc_client: Optional[IpcClient] = None
            self.client_thread: Optional[threading.Thread] = None
            self.loop: Optional[asyncio.AbstractEventLoop] = None
            self.is_running = False
            self.is_connected = False
            self._no_plugin_logged = False
            self._last_on_class_left_log_time = 0  # 上次记录距离上课时间的时间
            self._last_known_subject_name: Optional[str] = None

        def start_ipc_client(self) -> bool:
            """
            启动 C# IPC 客户端

            Returns:
                启动成功返回True，失败返回False
            """
            if self.is_running:
                return True

            try:
                self.is_running = True
                self.client_thread = threading.Thread(
                    target=self._run_client, daemon=False
                )
                self.client_thread.start()
                log.success("成功启动 C# IPC 客户端！")
                return True
            except Exception as e:
                self.is_running = False
                log.exception(f"启动 C# IPC 客户端失败: {e}")
                return False

        def stop_ipc_client(self):
            """停止 C# IPC 客户端"""
            log.debug("正在停止 C# IPC 客户端...")
            self.is_running = False
            if self.loop and self.loop.is_running():
                # 获取所有正在运行的任务并取消它们
                # 这会使 await asyncio.sleep(1) 等操作抛出 CancelledError
                try:
                    for task in asyncio.all_tasks(self.loop):
                        self.loop.call_soon_threadsafe(task.cancel)
                except Exception as e:
                    log.warning(f"取消 IPC 客户端任务时出错: {e}")

            if self.client_thread and self.client_thread.is_alive():
                # 给一点时间让线程退出，但不阻塞太久
                # 线程不是 daemon 的，这里只等待短时间以避免长时间阻塞主线程
                self.client_thread.join(timeout=0.5)
            log.debug("C# IPC 客户端停止请求已发出")

        def is_breaking(self) -> bool:
            """是否处于下课时间"""
            lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                self.ipc_client.Provider, self.ipc_client.PeerProxy
            )
            state = lessonSc.CurrentState in [
                getattr(TimeState, "None"),
                TimeState.PrepareOnClass,
                TimeState.Breaking,
                TimeState.AfterSchool,
            ]
            log.debug(
                f"获取到的 ClassIsland 时间状态: {lessonSc.CurrentState} 是否下课: {state}"
            )
            return state

        def get_on_class_left_time(self) -> int:
            """获取距离上课剩余时间（秒）

            Returns:
                int: 距离上课的剩余时间（秒），如果当前正在上课或没有下一节课程则返回0
            """
            try:
                import time

                lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                    self.ipc_client.Provider, self.ipc_client.PeerProxy
                )
                on_class_left_time = lessonSc.OnClassLeftTime
                total_seconds = int(on_class_left_time.TotalSeconds)

                # 根据距离上课的时间调整日志记录频率
                # 距离上课3秒前：每30秒记录一次
                # 距离上课3秒内：每秒记录一次
                current_time = time.time()
                should_log = False

                if total_seconds > 0 and total_seconds <= 3:
                    # 3秒内，每秒记录一次
                    should_log = True
                elif current_time - self._last_on_class_left_log_time >= 30:
                    # 3秒前，每30秒记录一次
                    should_log = True
                    self._last_on_class_left_log_time = current_time

                if should_log and total_seconds != 0:
                    log.debug(f"获取到的距离上课剩余时间: {total_seconds} 秒")

                return total_seconds
            except Exception as e:
                log.error(f"获取距离上课时间失败: {e}")
                return 0

        def get_current_class_info(self) -> dict:
            """获取当前课程信息

            Returns:
                dict: 课程信息字典，包含 name, start_time, end_time, teacher, location
                      如果当前没有课程或获取失败，返回空字典
            """
            try:
                if not self.is_running or not self.is_connected:
                    return {}

                lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                    self.ipc_client.Provider, self.ipc_client.PeerProxy
                )

                # 检查是否有当前课程
                if not lessonSc.CurrentSubject:
                    log.debug("ClassIsland 当前没有课程")
                    return {}

                # 获取课程名称
                class_name = (
                    lessonSc.CurrentSubject.Name if lessonSc.CurrentSubject else ""
                )
                # 如果获取到的是 class_name 为空 或者是 "???"，说明当前没有课程
                if not class_name or class_name.strip() == "???":
                    log.debug("ClassIsland 当前没有课程")
                    return {}
                log.info(f"从 ClassIsland 获取当前课程: {class_name}")
                self._last_known_subject_name = class_name
                return {"name": class_name}

            except Exception as e:
                log.error(f"从 ClassIsland 获取课程信息失败: {e}")
                return {}

        def get_next_class_info(self) -> dict:
            """获取下一节课的课程信息

            Returns:
                dict: 课程信息字典，包含 name, start_time, end_time, teacher, location
                      如果没有下一节课或获取失败，返回空字典
            """
            try:
                if not self.is_running or not self.is_connected:
                    return {}

                lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                    self.ipc_client.Provider, self.ipc_client.PeerProxy
                )

                # 检查是否有下一节课
                if not lessonSc.NextClassSubject:
                    log.debug("ClassIsland 没有下一节课")
                    return {}

                # 获取课程名称
                class_name = (
                    lessonSc.NextClassSubject.Name if lessonSc.NextClassSubject else ""
                )
                if not class_name or class_name.strip() == "???":
                    log.debug("ClassIsland 下一节课名称无效")
                    return {}

                log.info(f"从 ClassIsland 获取下一节课: {class_name}")
                return {"name": class_name}

            except Exception as e:
                log.error(f"从 ClassIsland 获取下一节课信息失败: {e}")
                return {}

        def get_previous_class_info(self) -> dict:
            if not self._last_known_subject_name:
                return {}
            if self._last_known_subject_name.strip() == "???":
                return {}
            return {"name": self._last_known_subject_name}

        def get_elapsed_since_previous_time_point_end_seconds(self) -> int:
            try:
                if not self.is_running or not self.is_connected:
                    return 0

                lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                    self.ipc_client.Provider, self.ipc_client.PeerProxy
                )

                current_index = int(lessonSc.CurrentSelectedIndex)
                if current_index <= 0:
                    return 0

                class_plan = lessonSc.CurrentClassPlan
                if not class_plan:
                    return 0

                valid_items = class_plan.ValidTimeLayoutItems
                if not valid_items:
                    return 0

                previous_item = valid_items[current_index - 1]
                end_time = previous_item.EndTime
                elapsed = DateTime.Now.TimeOfDay - end_time
                total_seconds = int(elapsed.TotalSeconds)
                return max(0, total_seconds)
            except Exception:
                return 0

        def _on_class_test(self):
            lessonSc = GeneratedIpcFactory.CreateIpcProxy[IPublicLessonsService](
                self.ipc_client.Provider, self.ipc_client.PeerProxy
            )
            try:
                if lessonSc.CurrentSubject and lessonSc.CurrentSubject.Name:
                    name = str(lessonSc.CurrentSubject.Name)
                    if name and name.strip() != "???":
                        self._last_known_subject_name = name
            except Exception:
                pass
            log.debug(
                f"上课 {lessonSc.CurrentSubject.Name} 时间: {lessonSc.CurrentTimeLayoutItem}"
            )

        def _run_client(self):
            """运行 C# IPC 客户端"""

            async def client():
                """异步客户端"""

                self.ipc_client = IpcClient()
                self.ipc_client.JsonIpcProvider.AddNotifyHandler(
                    IpcRoutedNotifyIds.OnClassNotifyId,
                    Action(lambda: self._on_class_test()),
                )

                task = self.ipc_client.Connect()
                await self.loop.run_in_executor(None, lambda: task.Wait())
                self.is_connected = True
                log.debug("C# IPC 连接成功！")

                while self.is_running:
                    await asyncio.sleep(.5)

                    # log.debug(f"stat: plugin({self._check_plugin_alive()}) ci({self._check_ci_alive()})")
                    if not self.check_ci_alive():
                        if not self.check_ci_alive():
                            log.debug("C# IPC 断连！重连...")
                            self.is_connected = False

                            task = self.ipc_client.Connect()
                            await self.loop.run_in_executor(
                                None, lambda task=task: task.Wait()
                            )
                            self.is_connected = True
                            log.debug("C# IPC 连接成功！")
                        elif not self._no_plugin_logged:
                            log.debug("未安装插件。")
                            self._no_plugin_logged = True
                    else:
                        self._no_plugin_logged = False

                self.ipc_client = None
                self.is_connected = False

            # 启动新的 asyncio 事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(client())
            except asyncio.CancelledError:
                pass
            except Exception as e:
                log.exception(f"C# IPC 客户端循环出错: {e}")
            finally:
                self.loop.close()
                self.loop = None

        def check_ci_alive(self) -> bool:
            """ClassIsland 是否正常连接"""
            try:
                lessonsService = GeneratedIpcFactory.CreateIpcProxy[
                    IPublicLessonsService
                ](self.ipc_client.Provider, self.ipc_client.PeerProxy)
                return lessonsService.IsTimerRunning
            except Exception as e:
                log.debug(e)
                return False

        @staticmethod
        def _safe_int(value: Any) -> int:
            try:
                if value is None:
                    return 0
                return int(value)
            except Exception:
                return 0

        def __enter__(self) -> "CSharpIPCHandler":
            if self.start_ipc_client():
                time.sleep(0.5)
                return self
            else:
                raise IPCError("ClassIsland IPC 客户端启动失败")

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop_ipc_client()
            if exc_type is not None:
                log.error(f"IPC 上下文中出现错误: {exc_type.__name__}: {exc_val}")
                log.debug(f"{traceback.format_tb(exc_tb)}")
                return False
            return True
else:
    class CSharpIPCHandler:
        """C# dotnetCampus.Ipc 处理器，用于连接 ClassIsland 实例"""

        _instance: Optional["CSharpIPCHandler"] = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

        @classmethod
        def instance(cls):
            """获取单例实例"""
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

        def __init__(self):
            """
            初始化 C# IPC 处理器
            """
            self.ipc_client = None
            self.client_thread = None
            self.is_running = False
            self.is_connected = False

        def start_ipc_client(self) -> bool:
            """
            启动 C# IPC 客户端

            Returns:
                启动成功返回True，失败返回False
            """
            return False

        def stop_ipc_client(self):
            """停止 C# IPC 客户端"""
            pass


        def is_breaking(self) -> bool:
            """是否处于下课时间"""
            return False

        def get_on_class_left_time(self) -> int:
            """获取距离上课剩余时间（秒）

            Returns:
                int: 距离上课的剩余时间（秒），如果当前正在上课或没有下一节课程则返回0
            """
            return 0

        def get_current_class_info(self) -> dict:
            """获取当前课程信息

            Returns:
                dict: 课程信息字典，包含 name, start_time, end_time, teacher, location
                      如果当前没有课程或获取失败，返回空字典
            """
            return {}

        def get_next_class_info(self) -> dict:
            """获取下一节课的课程信息

            Returns:
                dict: 课程信息字典，包含 name, start_time, end_time, teacher, location
                      如果没有下一节课或获取失败，返回空字典
            """
            return {}

        def get_previous_class_info(self) -> dict:
            return {}

        def get_elapsed_since_previous_time_point_end_seconds(self) -> int:
            return 0

        def _on_class_test(self):
            pass

        def _run_client(self):
            """运行 C# IPC 客户端"""
            pass

        def check_ci_alive(self) -> bool:
            """ClassIsland 是否正常连接"""
            return False

        def __enter__(self) -> CSharpIPCHandler:
            if self.start_ipc_client():
                return self
            else:
                raise IPCError("ClassIsland IPC 客户端启动失败")

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop_ipc_client()
            return False