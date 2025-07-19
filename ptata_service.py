import abc
import dataclasses
import json
import socket
import types




class Config:
    pass


class PTATServie:

    def __init__(self, sock: socket.socket):
        self._sock = sock

    def send_command(self, command: "Command"):
        self._sock.send(str(command).encode('utf-8'))
        # self._sock.recvfrom()

@dataclasses.dataclass
class CommandResult:
    command: str
    message: str
    status: str
    data: object





class Command(abc.ABC) :
    @abc.abstractmethod
    def command(self) -> str:
        pass


    def get_commend_result(self, service: PTATServie) -> CommandResult:
        service.send_command(self)
        pass


    @abc.abstractmethod
    def handle_result(self, service: PTATServie) -> CommandResult:
        pass

    def __str__(self):
        data = { "Command": self.command() }
        return json.dumps(data)

