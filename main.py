import asyncio
import logging
import os
import sys
from tkinter import messagebox
from commands.common import GetToolInfo
from commands.logging import StopLogging
from service import PTATService, MessageListener
from commands import GetLicenseStatus, MonitorView, AddToMonitorList, \
    RemoveFromMonitorList, GetMonitorData, StartMonitor, StopMonitor, \
    StartLogging, GetLogHeaderServer

from service.proxy import ProxyService

from ui import app
import utils


PTAT_LAUNCHER_PATH = "C:\\Program Files\\Intel Corporation\\Intel(R)PTAT\\PTATLauncher.exe"
PTAT_PATH = "C:\\Program Files\\Intel Corporation\\Intel(R)PTAT"


class MessageListenerImpl(MessageListener):

    def on_error(self, e: Exception):
        logging.error(f"error: {e}")
        return super().on_error(e)
    
    def on_message(self, message: str | bytes):
        logging.info(f"recv msg: ${message}")
        return super().on_message(message)

    def on_open(self):
        logging.info("opened ..")
        return super().on_open()


async def main_impl():
    service = PTATService("127.0.0.1", 64900, MessageListenerImpl())
    
    is_connected = await service.connect(timeout=5)
    if not is_connected:
        logging.error("can't connect to ptat!")
        sys.exit(1)

    result = await GetLicenseStatus().execute_and_get_result(service)
    print(f"result: {result}")

    result = await GetToolInfo().execute_and_get_result(service)
    print(f"result: {result}")

    await MonitorView().execute(service)

    result = await GetMonitorData().execute_and_get_result(service)
    # print(f"result: {result}")

    # result = await AddToMonitorList(params={"Args": "0"}).execute_and_get_result(service)
    # print(f"result: {result}")

    result = await GetLogHeaderServer().execute_and_get_result(service)
    print(f"result: {result}")

    result = await StartLogging().execute_and_get_result(service)
    print(f"result: {result}")

    result = await StartMonitor().execute_and_recv_result(service)
    
    await asyncio.sleep(1.5 * 60 * 60)
    # await service.keeping()
    # await asyncio.Event().wait()
    result = await StopLogging().execute_and_get_result(service)
    print(f"result: {result}")

    result = await StopMonitor().execute_and_get_result(service)
    print(f"result: {result}")



async def main_proxy_impl():
    service = ProxyService("127.0.0.1", proxy_port=64900, listen_port=64901)
    await service.start_proxy()




if __name__ == '__main__':
    if not utils.is_admin():
        messagebox.showerror("异常", "请用管理员身份运行！")
        sys.exit(1)
        
    app.main_loop()