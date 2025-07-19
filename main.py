import asyncio
import logging
import sys
from service import PTATService, MessageListener
from commands import GetLicenseStatus, MonitorView, AddToMonitorList, \
    RemoveFromMonitorList, GetMonitorData, StartMonitor, StopMonitor

PTAT_LAUNCHER_PATH = "C:\\Program Files\\Intel Corporation\\Intel(R)PTAT\\PTATLauncher.exe"

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

    await MonitorView().execute(service)

    result = await GetMonitorData().execute_and_get_result(service)
    print(f"result: {result}")

    result = await AddToMonitorList(params={"Args": "0"}).execute_and_get_result(service)
    print(f"result: {result}")

    result = await StartMonitor().execute_and_recv_result(service)
    
    # await service.keeping()
    await asyncio.Event().wait()
    

if __name__ == '__main__':
    asyncio.run(main_impl())
