from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Optional
import websockets
from commands import Command
from base import CommandExecutor, Response
from commands.base import MultiResponseCommand

class MessageListener(ABC):
    # ws 的消息监听
    @abstractmethod
    def on_open(self):
        pass

    @abstractmethod
    def on_error(self, e: Exception):
        pass

    @abstractmethod
    def on_message(self, message: websockets.Data):
        pass


class PTATService(CommandExecutor):
    """
    实现对 PTAT 工具的 websocket 链接，执行对应的命令。
    """
    __max_retry_count = 5

    def __init__(self, host: str, port: int, listener: MessageListener):
        super().__init__()
        self._listener = listener
        self._addr: str = f"ws://{host}:{port}/echo"
        self._msg_queue = asyncio.Queue[websockets.Data]()
        self._ws: Optional[websockets.ClientConnection] = None
        self._recv_task: Optional[asyncio.Task] = None

    async def connect(self, timeout: float) -> bool:
        if self._recv_task:
            return True
        for idx in range(0, self.__max_retry_count):
            try:
                self._ws = await asyncio.wait_for(
                    websockets.connect(
                        self._addr, 
                        ping_interval=1000, # 保活需要比较大的间隔和超时
                        ping_timeout=1000
                    ), 
                    timeout
                )
                self._ws.start_keepalive()
                self._recv_task = asyncio.create_task(self._recv_loop())
                self._listener.on_open()
                self.is_running = True
                return True
            except Exception as e:
                if idx == self.__max_retry_count - 1:
                    self._listener.on_error(e)
                elif idx > 0:
                    logging.warning("connect error, retrying ...")
                self._recv_task = None
                self.is_running = False
        return False
    
    async def execute_command(self, command: Command) -> bool:
        if not super().execute_command(command):
            return False
        assert self._ws is not None
        command_str = str(command)
        print(f"execute_command: {command_str}")
        await self._ws.send(command_str)
        return True
    
    async def recv_response(self) -> Response:
        return await self._msg_queue.get()

    async def _recv_loop(self):
        assert self._ws is not None
        try:
           while self._ws is not None:
                async for message in self._ws:
                    print("_recv_loop: {}".format(message[0:30]))
                    try: 
                        self._listener.on_message(message)
                        await self._msg_queue.put(message)
                    except Exception as e:
                        logging.exception(f"recv message error {e}")
        except Exception as e:
            logging.exception(f"fuck looping happen error!!!! {e}")

    async def keeping(self):
        if self._recv_task:
            await self._recv_task

    def _on_stop_executing_command(self, command: Command):
        if isinstance(command, MultiResponseCommand):
            command.stop_recv()

    async def shutdown(self):
        await super().shutdown()
        assert self._ws is not None
        assert self._recv_task is not None
        await self._ws.close()
        self._ws = None
        self._recv_task.cancel()
        self._recv_task = None