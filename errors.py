# pylint: disable=missing-docstring

from json.decoder import JSONDecodeError

class RequestError(Exception):
    def __init__(self, response):
        message = RequestError.__get_error_message(response)
        super().__init__(message)

    @staticmethod
    def create(response):
        if 400 <= response.status_code < 500:
            return ClientError(response)
        if 500 <= response.status_code < 600:
            return ServerError(response)
        return RequestError(response)

    @staticmethod
    def __get_error_message(response):
        try:
            error = response.json()['error']
            message = error.get('message', 'error occurred')
            tip = error.get('tip', 'fix the problem')
            return f'An error occurred\n{message}\n{tip}\nRequest url: {response.url}'
        except JSONDecodeError as error:
            return f'JSON decoding error: {error.msg}\n\nResponse content:\n\n{response.text}'

class ServerError(RequestError):
    pass

class ClientError(RequestError):
    pass
