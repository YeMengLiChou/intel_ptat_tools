
from typing import Literal, Optional, Union
from .result import GetSettingsResult, SettingsOption
from .base import EmptyResponseCommand, NoResponseCommand, OnceResponseCommand


class GetSettings(OnceResponseCommand[GetSettingsResult]):
    """
    读取配置进行初始化。
    """
    def _handle_command_msg(self, data: list) -> GetSettingsResult:
        data_dict = {
            item["Key"]: item["Value"] for item in data
        }
        result = GetSettingsResult()
        for key, set_key in (
            (SettingsOption.KEY_LOG_FILE_TYPE, SettingsOption.KEY_LOG_FILE_TYPE_SELECT),
            (SettingsOption.KEY_MEM_LOG_LEVEL, SettingsOption.KEY_MEM_LOG_LEVEL_SELECT),
            (SettingsOption.KEY_CPU_LOG_LEVEL, SettingsOption.KEY_CPU_LOG_LEVEL_SELECT),
            (SettingsOption.KEY_FILE_OPTION, SettingsOption.KEY_FILE_OPTION_SELECT),
            (SettingsOption.KEY_LOG_FILE_NAME, None),
            (SettingsOption.KEY_LOG_FILE_NAME_SERVER_CPU, None),
            (SettingsOption.KEY_LOG_FILE_NAME_SERVER_MEM, None),
            (SettingsOption.KEY_LOG_FILE_NAME_SERVER_PCH, None),
            (SettingsOption.KEY_POLLING_INTERVAL, None),
            (SettingsOption.KEY_REFRESH_INTERVAL, None),
            (SettingsOption.KEY_DISPLAY_HELP, None),
            (SettingsOption.KEY_RESULT_ALL, None),
            (SettingsOption.KEY_SYNC_PERIOD, None),
            (SettingsOption.KEY_APP_LOG_FILE_PATH, None),
            (SettingsOption.KEY_APP_LOG_FILE_TYPE, None),
            (SettingsOption.KEY_LOG_STATIC_DATA, None),

        ):
            result[key] = self.__create_settings_options(data_dict, key, set_key)
        return result
    
    @staticmethod
    def __create_settings_options(data: dict, key: str, set_key: Optional[str]) -> SettingsOption:
        return SettingsOption(
                key=key,
                set_key=set_key or key,
                option=data.get(key),
                value=data[set_key or key],
                is_camp_yes_value=key == SettingsOption.KEY_RESULT_ALL
            )


FileOption = Literal[
    "Append To Existing File",
    "Remove Old And Create",
    "Create New With Time Stamp"
]
class SetSettings(EmptyResponseCommand):
    """
    设置配置
    """
    def __init__(
            self, 
            log_file_type: Literal["csv", "html"] = "csv",
            mem_log_levl: Literal[0, 1, 2] = 0,
            cpu_log_level: Literal[0, 1, 2] = 0,
            file_option: FileOption = "Create New With Time Stamp",
            log_file_name: str = "PTATMonitor.csv",
            log_file_name_server_cpu: str = "PTATMonitorCPU.csv",
            log_file_name_server_mem: str = "PTATMonitorMEM.csv",
            log_file_name_server_pch: str = "",
            polling_interval_ms: int = 1000,
            refresh_interval_ms: int = 1000,
            dispaly_help: bool = True,
            reset_all: bool = True,
            sync_period: int = 1000,
            app_log_file_path: str = "PTATAppEvents.csv",
            app_log_file_type: Literal["csv", "html"] = "csv",
            log_static_data: bool = True
    ) -> None:
        params = {
            SettingsOption.KEY_LOG_FILE_TYPE_SELECT: log_file_name,
            SettingsOption.KEY_MEM_LOG_LEVEL_SELECT: mem_log_levl,
            SettingsOption.KEY_CPU_LOG_LEVEL_SELECT: cpu_log_level,
            SettingsOption.KEY_FILE_OPTION_SELECT: file_option,
            SettingsOption.KEY_LOG_FILE_NAME_SERVER_CPU: log_file_name_server_cpu,
            SettingsOption.KEY_LOG_FILE_NAME_SERVER_MEM: log_file_name_server_mem,
            SettingsOption.KEY_LOG_FILE_NAME_SERVER_PCH: log_file_name_server_pch,
            SettingsOption.KEY_POLLING_INTERVAL: polling_interval_ms,
            SettingsOption.KEY_REFRESH_INTERVAL: refresh_interval_ms,
            SettingsOption.KEY_DISPLAY_HELP: "yes" if dispaly_help else "no",
            SettingsOption.KEY_RESULT_ALL: "Yes" if reset_all else "No",
            SettingsOption.KEY_SYNC_PERIOD: sync_period,
            SettingsOption.KEY_APP_LOG_FILE_PATH: app_log_file_path,
            SettingsOption.KEY_APP_LOG_FILE_TYPE: app_log_file_type,
            SettingsOption.KEY_LOG_STATIC_DATA: 1 if log_static_data else 0
        }
        super().__init__(params)