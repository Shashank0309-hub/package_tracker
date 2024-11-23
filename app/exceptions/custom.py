from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class CommonException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ClientException(CommonException):
    def __init__(self, message, status_code=HTTP_500_INTERNAL_SERVER_ERROR, data=None):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)


class SearchException(ClientException):
    pass


class NoResultException(ClientException):
    pass
