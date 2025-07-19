import asyncio
import json
from typing import Generic, List, Optional, TypeVar
from abc import abstractmethod
from dataclasses import dataclass
from base import Command, CommandExecutor, Response
from .result import EmptyResult

class NoResponseCommand(Command):
    """
    无回复命令
    """
    async def execute(self, executor: CommandExecutor) -> bool:
        return await self._execute(executor)
    

_T = TypeVar("_T")


@dataclass
class CommandResult(Generic[_T]):
    """
    命令对应的回复结果
    """
    command: str
    message: str
    status: str
    data: _T

    def is_success(self) -> bool:
        return self.status == "Success"


class ResponseCommand(Command, Generic[_T]):
    """
    有回复的命令
    """
    
    def _handle_response(self, response: Response) -> CommandResult[_T]:
        print(f"[{self.get_command_name()}] parse response, {response[0:30]}")
        data: dict = json.loads(response)

        command = data["Command"]
        command_status = data["CommandStatus"]
        message = command_status["Message"]
        status = command_status["Status"]
        handled_data: _T = self._handle_command_msg(
            data["Data"] if data.__contains__("Data") else []
        )
        return CommandResult(command, message, status, handled_data)

    @abstractmethod
    def _handle_command_msg(self, data: list) -> _T:
        pass


class OnceResponseCommand(ResponseCommand[_T]):
    """
    一对一的命令
    """
    async def execute_and_get_result(self, executor: CommandExecutor) -> Optional[CommandResult[_T]]:
        executed = await self._execute(executor)
        if not executed:
            return None
    
        response = await executor.recv_response() 
        return self._handle_response(response)


class MultiResponseCommand(ResponseCommand[_T]):
    """
    一对多的命令
    """

    def __init__(self):
        super().__init__()
        self.result_list: List[CommandResult[_T]] = []
        self.recv_task: Optional[asyncio.Task] = None

    async def execute_and_recv_result(self, executor: CommandExecutor) -> bool:
        self.stop_recv()
        executed = await self._execute(executor)
        if not executed:
            return False
        
        self.recv_task = asyncio.create_task(
            self.__recv_multi_response(executor)
        )
        return True

    async def __recv_multi_response(self, executor: CommandExecutor):
        while executor.executing_command == self:
            self.result_list.append(
                self._handle_response(await executor.recv_response())
            )
        
    def stop_recv(self):
        if self.recv_task:
            self.recv_task.cancel()
            self.recv_task = None


class EmptyResponseCommand(OnceResponseCommand[EmptyResult]):
    """
    没有 Data 字段的命令
    """
    def _handle_command_msg(self, data: List) -> EmptyResult:
        return EmptyResult()