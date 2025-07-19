import json
import logging
import asyncio
from abc import ABC
from typing import Optional
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union

__all__ = (
    "Command",
    "CommandExecutor",
    "Response"
)


class Command(ABC):

    def __init__(self, params: Optional[dict] = None) -> None:
        super().__init__()
        self._params: Optional[dict] = params

    def get_command_name(self) -> str:
        return self.__class__.__name__
    
    def _submit(self, executor: "CommandExecutor") -> bool:
        if not executor.is_running:
            return False
        try:
            return executor.submit_command(self)
        except Exception as e:
            logging.exception("commend execute failed, cause by {}".format(e),)
            return False
  
    async def _execute(self, executor: "CommandExecutor") -> bool:
        if not executor.is_running:
            return False
        try:
            await executor.execute_command(self)
            return True
        except Exception as e:
            logging.exception("commend execute failed, cause by {}".format(e))
            return False
    
    def __str__(self):
        data: dict = { "Command": self.get_command_name() }
        if self._params is not None and len(self._params) > 0:
            data["params"] = self._params
        return json.dumps(data)


Response = Union[str, bytearray, bytes]

_RES = TypeVar("_RES")

class CommandExecutor(ABC, Generic[_RES]):
    """
    执行命令的基类
    """

    def __init__(self) -> None:
        super().__init__()
        self.executing_command: Optional[Command] = None
        self.is_running: bool = False
        
    @abstractmethod
    async def execute_command(self, command: Command) -> bool:
        if not self.is_running:
            return False
        self._stop_executing_command()
    
    def submit_command(self, command: Command) -> bool:
        if not self.is_running:
            return False
        asyncio.run(self.execute_command(command))
        return True

    @abstractmethod
    async def recv_response(self) -> Response:
        pass

    def _stop_executing_command(self):
        if self.executing_command:
            self._on_stop_executing_command(self.executing_command)
            self.executing_command = None

    @abstractmethod
    def _on_stop_executing_command(self, command: Command):
        pass

    @abstractmethod
    async def shutdown(self):
        self.is_running = False
        self._stop_executing_command()
        pass