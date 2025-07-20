import json
import os
from typing import Any, Callable, Dict, Optional, TypeVar
import asyncio
import aiofiles


SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "config.json")

PTAT_DEFAULT_PATH = "C:\\Program Files\\Intel Corporation\\Intel(R)PTAT"

_A = TypeVar("_A")
_B = TypeVar("_B")


class ObservableDict(Dict[_A, _B]):

    def __init__(self, on_change: Callable):
        self._on_change = on_change

    def __getitem__(self, key: Any) -> Any:
        return super().__getitem__(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        changed = True
        if self.__contains__(key) and self.__getitem__(key) is value:
            changed = False

        super().__setitem__(key, value)
        if changed:
            self._on_change()

    def __delitem__(self, key: _A) -> None:
        super().__delitem__(key)
        self._on_change()



class AppConfig:

    def __init__(self, settings_path: str):
        self._settings_path = settings_path
        self._data = ObservableDict[str, any](self.__handle_config_change)
        self._is_loading = False
        asyncio.run(self.__load_config(self._data))
        

    async def __load_config(self, data: ObservableDict):
        self._is_loading = True
        if not os.path.exists(self._settings_path):
            async with aiofiles.open(self._settings_path, mode="w", encoding="utf-8") as f:
                json.dump(data, f)
        else:
             async with aiofiles.open(self._settings_path, mode="r", encoding="utf-8") as f:
                file_content = await f.read()
                print(file_content)
                data.update(json.loads(file_content))
        self._is_loading = False


    def __handle_config_change(self):
        if self._is_loading:
            return
        asyncio.run(self.__save(self._data))

    async def __save(self, data: ObservableDict):
        async with aiofiles.open(self._settings_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data))

    def get_ptat_path(self) -> str:
        path = self._data.get("ptat_path")
        if isinstance(path, str):
            return path
        else:
            self.set_ptat_path(PTAT_DEFAULT_PATH)
            return PTAT_DEFAULT_PATH
        

    def set_ptat_path(self, path: str):
        self._data["ptat_path"] = path
        


config = AppConfig(SETTINGS_PATH)
