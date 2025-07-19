import ctypes
import logging
import sys
from typing import Optional
import socket
import websocket

import utils
import ptata_service

PTAT_LAUNCHER_PATH = "\C:\Program Files"
PORT_NUMBER = 64900
SOCKET_ADDR = f"localhost:{PORT_NUMBER}/echo"
SOCKET_TIMEOUT_SECONDS = 5
MAX_RETRY_COUNT = 3

def connect_socket() -> Optional[socket.socket]:
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.settimeout(SOCKET_TIMEOUT_SECONDS)
    is_connected = False
    retry_count = 0
    while not is_connected and retry_count < MAX_RETRY_COUNT:
        connect_status = sc.connect_ex(SOCKET_ADDR)
        is_connected = connect_status == 0
        retry_count += 1

    if not is_connected:
        return None
    return sc




def main_impl():
    if not utils.is_admin():
        logging.error("请以管理员权限运行")
        sys.exit(1)

    # 启动
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, )
    # 等待
    if sc := connect_socket():
        logging.error("连接 ptat 工具失败！请重试！")
        sys.exit(1)

    service = ptata_service.PTATServie(sc)




if __name__ == '__main__':
    main_impl()
