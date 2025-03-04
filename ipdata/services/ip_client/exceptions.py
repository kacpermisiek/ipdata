class IpStackException(Exception):
    def __init__(self, code: int, err_type: str, info: str):
        self.code = code
        self.type = err_type
        self.info = info
