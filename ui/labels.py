import tkinter as tk
from tkinter import ttk
from enum import Enum
from typing import Literal


class StatusIndicator(tk.Frame):
    
    SUCCESS = 1
    ERROR = 0

    def __init__(self, init_status: Literal[0, 1] = 0, size: int = 20, **kwargs):
        super().__init__(width=size, height=size, **kwargs)
        self.status = init_status
        # 禁止自动收缩
        self.pack_propagate(False)

    def _get_color_by_status(self) -> str:
        match self._status:
            case StatusIndicator.ERROR:
                return "#ff1744"
            case StatusIndicator.SUCCESS:
                return "#2ed573"
        return "#ff1744"
    
    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, value: Literal[0, 1]):
        self._status = value
        self.config(bg=self._get_color_by_status())
