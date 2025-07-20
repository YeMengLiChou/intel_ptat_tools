import asyncio
import logging
from typing import Optional

import websockets


class ProxyService:
    """
    代理PTAT主程序与网页之间的通信，进而可以解析命令返回值以及拦截和模拟一些操作
    **简单实现**
    """

    def __init__(self, host: str, proxy_port: int, listen_port: int ) -> None:
        self._host = host
        self._listen_port = listen_port
    
        self._proxy_addr = f"ws://{host}:{proxy_port}/echo"
        self._is_running = False
        self._proxy_task: Optional[asyncio.Task] = None
        self._listen_ws: Optional[websockets.Server] = None
        self._proxy_ws: Optional[websockets.ClientConnection] = None
        self._pending_send_queue: asyncio.Queue[websockets.Data] = asyncio.Queue(10)
        self._pending_recv_queue: asyncio.Queue[websockets.Data] = asyncio.Queue(10)

    async def start_proxy(self):
        self._listen_ws = await websockets.serve(
                self._handle_listen_ws, 
                self._host, 
                self._listen_port, 
                ping_interval=1000, 
                ping_timeout=1000
            )
        print("created proxy ws successfullyy!")
        
        for retry_idx in range(5):
            try:
                self._proxy_ws = await asyncio.wait_for(
                    websockets.connect(
                        self._proxy_addr,
                        ping_interval=1000, 
                        ping_timeout=1000
                    ), 5
                )
            except Exception as e:
                if retry_idx == 4:
                    logging.error("can't connect to target ws! cause by: {}".format(e))
                else:
                    logging.error("retry connect to proxyed ws, cause by: {}".format(e))
                    await asyncio.sleep(1)
        
        if self._proxy_ws is None:
            return 
        
        print("start proxy target ws!")
        asyncio.create_task(self._handle_pending_recv_msg())
        asyncio.create_task(self._handle_pending_send_msg())
        asyncio.create_task(self._handle_proxy_ws())
        await self._listen_ws.serve_forever()
        

    async def _handle_listen_ws(self, webscoket: websockets.ServerConnection):
        print("client connected!")
        while True:
            msg = await webscoket.recv()
            print("recv msg: {}. send it!".format(msg))
            await self._pending_send_queue.put(msg)

    async def _handle_proxy_ws(self):
        assert self._proxy_ws is not None
        try:
           while self._proxy_ws is not None:
                async for message in self._proxy_ws:
                    print("proxy recv msg: {}".format(message[0:30]))
                    try: 
                        await self._pending_recv_queue.put(message)
                    except Exception as e:
                        logging.exception(f"recv message error {e}")
        except Exception as e:
            logging.exception(f"fuck looping happen error!!!! {e}")

    async def _handle_pending_send_msg(self):
        while True:
            try:
                msg = await self._pending_send_queue.get()
                if msg is None:
                    print("send queue quit!")
                    break
                assert self._proxy_ws is not None
                print("proxy send msg {} sucessfully!".format(msg))
                asyncio.create_task(self._proxy_ws.send(msg))
            finally:
                self._pending_send_queue.task_done()

    async def _handle_pending_recv_msg(self):
        while True:
            try:
                msg = await self._pending_recv_queue.get()
                if msg is None:
                    print("send queue quit!")
                    break
                assert self._listen_ws is not None
                print("proxy recv msg {} sucessfully!".format(msg[0:30]))
                for conn in self._listen_ws.connections:
                    await conn.send(msg)
            finally:
                pass