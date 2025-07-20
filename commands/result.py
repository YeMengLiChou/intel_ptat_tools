from dataclasses import dataclass
from typing import List, Literal, Optional, Union
from enum import Enum
@dataclass
class EmptyResult:
    pass


@dataclass
class GetLicenseStatusResult:
    is_tool_license: bool
    is_telemetry_license: bool


@dataclass
class MonitorEntryParam:
    feature: str
    group_name: str
    name: str
    reader: str
    type: str
    uid: int
    unit: str


@dataclass
class MonitorEntry:
    is_graph_enable: bool
    index: int
    name: str
    param: MonitorEntryParam
    row: str
    is_selected: bool
    unit: str



@dataclass
class MonitorSubCategroy:
    header: str
    index: int
    name: str
    tooltip: str
    sub_tree_list: list[MonitorEntry]
    is_selected: bool

@dataclass
class MonitorMainCategroy:
    header: str
    index: int
    name: str
    tooltip: str
    is_selected: bool
    tree_list: list["MonitorSubCategroy"]


@dataclass
class GetMonitorDataResult:
    header: str
    index: int
    name: str
    tooltip: str
    tree_list: list["MonitorMainCategroy"]
    is_closed: bool
    is_selected: bool


@dataclass 
class StartMonitorResult(dict[int, str]):
    pass



@dataclass
class SettingsOption:
    key: str 
    set_key: str # 设置写入的所用的key
    option: Optional[Union[List[str], List[int]]]
    value: Union[str, int]
    is_camp_yes_value: bool = False
    
    # ==== constants ==== 
    KEY_LOG_FILE_TYPE = "LogFileType"
    KEY_LOG_FILE_TYPE_SELECT = "LogFileTypeSelected"
    KEY_MEM_LOG_LEVEL = "MEM Log Level"
    KEY_MEM_LOG_LEVEL_SELECT = "MEMLogLevelUserSelection"
    KEY_CPU_LOG_LEVEL = "CPULogLevel"
    KEY_CPU_LOG_LEVEL_SELECT = "CPULogLevelUserSelection"
    KEY_FILE_OPTION = "FileOption"
    KEY_FILE_OPTION_SELECT = "FileOptionSelected"
    KEY_LOG_FILE_NAME = "LogFileName"
    KEY_LOG_FILE_NAME_SERVER_CPU = "logfileNameServerCpu"
    KEY_LOG_FILE_NAME_SERVER_MEM = "logfileNameServerMem"
    KEY_LOG_FILE_NAME_SERVER_PCH = "logfileNameServerPch"
    KEY_POLLING_INTERVAL = "PollingInterval"
    KEY_REFRESH_INTERVAL = "RefreshInterval"
    KEY_DISPLAY_HELP = "DispalyHelp"
    KEY_RESULT_ALL = "ResetAll"
    KEY_SYNC_PERIOD = "SyncPeriod"
    KEY_APP_LOG_FILE_PATH = "AppLogFilePath"
    KEY_APP_LOG_FILE_TYPE = "AppLogFileType"
    KEY_LOG_STATIC_DATA = "LogStaticData"


@dataclass
class GetSettingsResult(dict[str, SettingsOption]):
    pass


class ToolInfo(Enum):   
    DEFAULT_PATH = "DefaultPath"
    CURRENT_IP_ADDRESS = "CurrentIpAddress"
    WORK_SPACE_PATH = "WorkSpacePath"
    OPERATING_SYSTEM = "OperatingSystem"
    SCRIPT_FILE_PATH = "ScriptFilePath"
    LOG_PATH = "LogPath"
    ALERT_PATH = "AlertPath"
    INSTALLED_PATH = "InstalledPath"
    IS_TELEMETRY_LICENSE_AGREED = "IsTelemetryLicenseAgreed"
    IS_TELEMETRY_ENABLED = "IsTelemetryEnabled"
    OS_VERSION = "OSVersion"
    PLATFORM_SKU = "platform_sku"
    SHOW_CONTROL_WARNING = "ShowControlWarning"


@dataclass
class GetToolInfoResult(dict[str, str]):
    pass