from .base import EmptyResponseCommand


class GetLogHeaderServer(EmptyResponseCommand):
    """
    start-logging前需要调用，应该是进行一些初始化操作。
    """
    pass


class StartLogging(EmptyResponseCommand):
    """
    开始记录日志
    """
    pass


class StopLogging(EmptyResponseCommand):
    """
    结束记录日志
    """