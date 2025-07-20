from dataclasses import dataclass
from .result import GetLicenseStatusResult, GetToolInfoResult
from .base import OnceResponseCommand


class GetLicenseStatus(OnceResponseCommand[GetLicenseStatusResult]):
    """
    初始化时获取许可证的状态
    """

    def _handle_command_msg(self, data: list) -> GetLicenseStatusResult:
        result = GetLicenseStatusResult(False, False)
        for item in data:
            key = item["Key"]
            value = item["Value"]
            if key == "ToolLicense":
                result.is_tool_license = value == 1
            elif key == "TelemetryLicense":
                result.is_telemetry_license = value == 1
        return result
    


class GetToolInfo(OnceResponseCommand[GetToolInfoResult]):

    def _handle_command_msg(self, data: list) -> GetToolInfoResult:
        data_dict =  {
            str(item["Key"]): str(item["Value"]) for item in data
        }
        result = GetToolInfoResult()
        result.update(data_dict)
        return result