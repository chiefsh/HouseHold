class InternalError(Exception):
    """应用层统一的异常"""
    def __init__(self, msg='内部错误', code=-1):
        self.code = code
        self.msg = msg


class NotFound(InternalError):
    """未找到指定项"""


class FileTypeError(InternalError):
    """文件类型错误"""


class Duplicate(InternalError):
    """重复项"""

    def __init__(self, msg="已存在", code=-1, duplicate=None):
        self.duplicate = duplicate
        super().__init__(msg, code)


class PermissionDenied(InternalError):
    """拒绝授权"""


class ParametersError(InternalError):
    """参数错误"""
