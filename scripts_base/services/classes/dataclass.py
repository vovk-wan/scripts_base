class DataStructure:

    def __init__(
            self: 'DataStructure',
            status: int = 200,
            code: str = '000000',
            success: bool = False,
            message: str = '',
            data: dict = None,
            # work_key: str = '',
    ) -> None:
        self.status: int = status
        self.code: str = code
        self.success: bool = success
        self.message: str = message
        self.data: dict = data or dict()
        # self.work_key: str = work_key

    def as_dict(self) -> dict:
        return self.__dict__
