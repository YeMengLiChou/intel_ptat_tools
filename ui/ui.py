import asyncio
import os
import threading
import tkinter as tk
from tkinter import StringVar, ttk, filedialog
from tkinter import messagebox
from typing import Any, Callable, List, Literal, Optional
from commands.common import GetLicenseStatus, GetToolInfo
from commands.monitor import GetMonitorData, MonitorView
from config import config
from service.ptat import PTATService
import utils
from utils.ptat_files_handle import PTATFiles
from .labels import StatusIndicator
from . import EventDispatcher, EventObserver


EVENT_PTAT_PATH_UPDATE = "ptat_path_update"
EVENT_PTAT_MAIN_JS_EXTRACT = "ptat_main_js_extract"

FONT_TITLE = [24]
FONT_NORMAL = [12]


class EventObserverImpl(EventObserver):
    def __init__(self, event_name: str, on_event: Callable):
        self._event_name = event_name
        self._on_event = on_event

    def on_event(self, *args):
        self._on_event(*args)

    def event_name(self) -> str:
        return self._event_name


class Application:

    def __init__(self, window: tk.Tk):
        self.window = window
        self.dispatcher = EventDispatcher()
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.thread = threading.Thread(target=self.event_loop.run_forever, daemon=True)
        self.thread.start()
        self.cur_port_number = -1
        self.is_main_loop_running = False
        self.pending_events: List[tuple[str, Any]] = []
        
        self.ptat_files: Optional[PTATFiles] = None
        self.ptat_service: Optional[PTATService] = None
        self.is_service_running = False
        
        self._init_weights()
        self._init_observers()

    def _init_weights(self):
        self._init_ptat_fold_choose()
        self._init_ptat_info()
        self._init_ptat_operations()
        
    def _init_observers(self):
        self.dispatcher.register_observer(
            EventObserverImpl(EVENT_PTAT_PATH_UPDATE, self.__handle_event_ptat_path_update)
        )
        self.dispatcher.register_observer(
            EventObserverImpl(EVENT_PTAT_MAIN_JS_EXTRACT, self.__handle_event_extract_js_port)
        )
        
        
    def __handle_event_ptat_path_update(self,  *args):
        self.addr_label.config(text="PTAT目录：{}".format(args[0]))
        self.path_status.status = StatusIndicator.SUCCESS

    def __handle_event_extract_js_port(self, *args):
        port_number = args[0]
        self.cur_port_number = port_number
        self.cur_port_show_label.config(
            text=f"{port_number}" if port_number > 0 else "端口解析异常"
        )

    def _init_ptat_fold_choose(self):
        path = config.get_ptat_path()
        is_exist = False
        try:
            is_exist = self.ptat_files = utils.locate_ptat_files_ex(path)
        except Exception as e:
            print("init ptat error {}".format(e))

        container = tk.LabelFrame(
            self.window, text="PTAT路径", font=FONT_TITLE
        )
        container.pack(fill="x", side="top", expand=True, padx=6, ipady=6)

        path_status = StatusIndicator(
            (StatusIndicator.ERROR if not is_exist else StatusIndicator.SUCCESS),
            master=container,
        )
        self.path_status = path_status
        path_status.pack(fill="none", side="left", expand=False, padx=8)

        addr_label = tk.Label(
            container, text="PTAT Directory：{}".format(path), font=FONT_NORMAL
        )
        self.addr_label = addr_label
        addr_label.pack(fill="none", side="left", expand=False)

        choose_btn = ttk.Button(
            container, text="选择文件夹", command=self.__handle_btn_choose_fold
        )
        choose_btn.pack(fill="none", side="right", expand=False, padx=6)

    def __handle_btn_choose_fold(self):
        """
        选择文件夹
        """
        path = filedialog.askdirectory(
            title="选择文件夹", mustexist=True, parent=self.window
        )
        try:
            self.ptat_files = utils.locate_ptat_files_ex(path)
            self.__dispatch(EVENT_PTAT_PATH_UPDATE, self.ptat_files.ptat_path)
        except Exception as e:
            messagebox.showerror("所选文件夹存在问题", message=str(e))

    def _init_ptat_info(self):
        """
        解析 PTAT 相关信息
        """
        is_extracting = False
        if self.ptat_files is not None:
            # 异步解析 js 文件的端口号
            is_extracting = True
            asyncio.run_coroutine_threadsafe(
                utils.extract_ptat_main_js_port(self.ptat_files.main_js_path),
                self.event_loop,
            ).add_done_callback(
                lambda t: self.__dispatch(
                    EVENT_PTAT_MAIN_JS_EXTRACT, t.result() if not t.cancelled() else 0
                )
            )

        container = tk.LabelFrame(self.window, text="PTAT Information", font=FONT_TITLE)
        container.pack(side="top", fill="x", expand=True)
        container.grid_columnconfigure(index=[0, 1, 2, 3, 4, 5], weight=1)

        tk.Label(
            container, text="当前端口：", font=FONT_NORMAL
        ).grid(row=0, column=0, columnspan=1, sticky="NSWE")

        self.cur_port_show_label = cur_port_show_label = tk.Label(
            container,
            text="加载中..." if is_extracting else "",
            state="disabled",
            font=FONT_NORMAL,
        )
        cur_port_show_label.grid(row=0, column=1, columnspan=2, sticky="NSW")
            
        tk.Label(container, text="更新端口(0~65535)", font=FONT_NORMAL).grid(
            row=0, column=3, padx=4, pady=4, sticky="NSWE"
        )

        change_port_str = StringVar(value="64901")
        change_port_input = tk.Entry(
            container, textvariable=change_port_str, font=FONT_NORMAL
        )
        change_port_input.event_delete
        change_port_input.grid(
            row=0, column=4, columnspan=2, padx=4, pady=4, sticky="NSWE"
        )

        # 更新端口展示以及字段
        def handle_done_update_port(t, update_port: int):
            if t.cancelled():
                return
            success = t.result()
            if success:
                self.cur_port_number = update_port
                self.__handle_event_extract_js_port((update_port))
                messagebox.showinfo("更新成功")
            else:
                messagebox.showwarning("异常", "更改失败！")

        # 点击更新
        def handle_update_port():
            if self.ptat_files is None:
                return
            value = int(change_port_str.get())

            asyncio.run_coroutine_threadsafe(
                utils.update_main_js_port_number(
                    self.ptat_files.main_js_path, self.cur_port_number, value
                ),
                self.event_loop,
            ).add_done_callback(lambda f: handle_done_update_port(f, value))

        change_btn = tk.Button(
            container, text="更新", state="disabled", command=handle_update_port
        )
        change_btn.grid(row=0, column=6, columnspan=1, padx=4, pady=4)

        # 输入时验证是否合法
        def validate_port_and_update_btn(_: str, __: str, ___: str):
            value = change_port_str.get()
            valid = (
                value.isnumeric()
                and (value := int(value)) in range(0, 65535)
                and value != self.cur_port_number
            )
            if valid:
                change_btn.config(state="active")
            else:
                change_btn.config(state="disabled")

        change_port_str.trace_add("write", validate_port_and_update_btn)
        
    def _init_ptat_operations(self):
        container = tk.LabelFrame(
            self.window, text="PTAT Actions", font=FONT_TITLE
        )
        container.pack(fill="x", side="top", expand=True, padx=6, ipady=4, ipadx=10)
        container.columnconfigure([0, 1, 2, 3], weight=1)
        container.columnconfigure([0, 1], pad=30)
        
        launcher_btn = tk.Button(container, text="启动PTAT", font=FONT_NORMAL, command=self.__handle_launch_ptat)
        launcher_btn.grid(row=0, column=0)
        
        logging_checkbox = tk.Checkbutton(container, text="记录日志", font=FONT_NORMAL)
        logging_checkbox.grid(row=0, column=1)
        
        start_monitor_btn = tk.Button(container, text="Start Monitor", font=FONT_NORMAL)
        start_monitor_btn.grid(row=1, column=0)
        
        stop_monitor_btn = tk.Button(container, text="Stop Monitor", font=FONT_NORMAL)
        stop_monitor_btn.grid(row=1, column=1)
        
    
    
    def __handle_launch_ptat(self):
        if self.ptat_files is None:
            messagebox.showerror("异常", "PTAT 路径异常！")
            return
        print("try launch launcher: {}".format(self.ptat_files.launcher_path))
        
        try:
            os.startfile(self.ptat_files.launcher_path) 
        except:
            messagebox.showerror("异常", "PTAT Launcher 启动失败！")
            return 
          
        messagebox.showinfo("启动中", "正在启动 PTAT 程序，网页打开无响应是正常现象！")
        self.ptat_service = PTATService("127.0.0.1", 64900)
        asyncio.run_coroutine_threadsafe(
            self.__connect_ptat_service(service=self.ptat_service),
            self.event_loop
        )
        
    async def __connect_ptat_service(self, service: PTATService):
        is_connected = await service.connect(timeout=5)
        if not is_connected:
            messagebox.showerror("连接失败", "连接 PTAT 失败！")
            return 
        self.is_service_running = True
        result = await GetLicenseStatus().execute_and_get_result(service)
        result = await GetToolInfo().execute_and_get_result(service)
        await MonitorView().execute(service)
        result = await GetMonitorData().execute_and_get_result(service)
            

    def __dispatch(self, event_name: str, *args):
        if self.is_main_loop_running:
            self.window.after(0, lambda: self.dispatcher.dispatch_event(event_name, *args))
        else:
            self.pending_events.append((event_name, args))
            
    def main_loop(self):
        self.is_main_loop_running = True
        if len(self.pending_events) > 0:
            def handle_pending_events():
                for event_name, event in self.pending_events:
                    self.dispatcher.dispatch_event(event_name, *event)
            self.window.after_idle(handle_pending_events)
        self.window.mainloop()


def _init_window(window: tk.Tk):
    window.title("PTAT 小助手")
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    window.resizable(True, True)
    window.wm_minsize(int(screen_w / 2), int(screen_h / 2))
    window.attributes("-topmost", True)


window = tk.Tk()
_init_window(window)
app = Application(window)
