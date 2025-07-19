from .result import GetMonitorDataResult, MonitorEntry, MonitorEntryParam, MonitorMainCategroy, MonitorSubCategroy, StartMonitorResult
from .util import parse_bool, parse_int
from .base import EmptyResponseCommand, MultiResponseCommand, NoResponseCommand, OnceResponseCommand

class MonitorView(NoResponseCommand):
    """
    点击 Monitor Tab 时发送的命令
    """

       
class AddToMonitorList(EmptyResponseCommand):
    """
    添加需要监控的选项
    """


class RemoveFromMonitorList(EmptyResponseCommand):
    """
    移除需要监控的选项
    """
      

class GetMonitorData(OnceResponseCommand[GetMonitorDataResult]):
    """
    获取所有监控的选项
    """
    def _handle_command_msg(self, data: list) -> GetMonitorDataResult:
        all_data = data[0]
        result = GetMonitorDataResult(
            header = all_data["Header"],
            index = parse_int(all_data["Index"]),
            name = all_data["Name"],
            tooltip= all_data["ToolTip"],
            tree_list=[],
            is_closed=parse_bool(all_data["isClosed"]),
            is_selected=parse_bool(all_data["isSelected"])
        )
        tree_list = all_data["Treelist"]
        for item in tree_list:
            item_result = MonitorMainCategroy(
                header = item["Header"],
                index = parse_int(item["Index"]),
                name = item["Name"],
                tooltip= item["ToolTip"],
                tree_list=[],
                is_selected=parse_bool(item["isSelected"])
            )
            result.tree_list.append(item_result)

            for sub_item in item["Treelist"]:
                sub_item_result = MonitorSubCategroy(
                    header = sub_item["Header"],
                    index = parse_int(sub_item["Index"]),
                    name = sub_item["Name"],
                    tooltip= sub_item["ToolTip"],
                    sub_tree_list=[],
                    is_selected=parse_bool(sub_item["isSelected"])
                )
                item_result.tree_list.append(sub_item_result)

                for entry_item in sub_item["SubTreeList"]:
                    param_dict = entry_item["Param"]
                    param = MonitorEntryParam(
                        feature=param_dict["feature"],
                        group_name=param_dict["groupName"],
                        name=param_dict["name"],
                        reader=param_dict["reader"],
                        type=param_dict["type"],
                        uid=parse_int(param_dict["uid"]),
                        unit=param_dict["unit"]
                    )

                    entry_result = MonitorEntry(
                        is_graph_enable=parse_bool(entry_item["GraphEnabled"]),
                        index=parse_int(entry_item["Index"]),
                        name=entry_item["Name"],
                        row=entry_item["Row"],
                        is_selected = parse_bool(entry_item["isSelected"]),
                        param=param,
                        unit=entry_item["unit"]
                    )
                    sub_item_result.sub_tree_list.append(entry_result)

        return result
    

class StartMonitor(MultiResponseCommand[StartMonitorResult]):
    """
    开始观测数据
    """

    def _handle_command_msg(self, data: list) -> StartMonitorResult:
        result = StartMonitorResult()
        for item in data:
            key = parse_int(item["Key"])
            result[key] = item["Value"]
        return result


class StopMonitor(EmptyResponseCommand):
    """
    结束观测数据
    """