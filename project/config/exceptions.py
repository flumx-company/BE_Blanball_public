from typing import Optional, Union, final

from django.utils.encoding import force_str
from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)


@final
class _404(APIException):

    status_code: int = HTTP_404_NOT_FOUND
    default_detail: str = "{object_name} not found."

    def __init__(self, *, object=None, detail: Optional[Union[dict[str, str]]] = None):
        if object is None and detail is None:
            raise Exception("detail or object must be set")
        if detail is None:
            detail = force_str(self.default_detail).format(object_name=object.__name__)
        super().__init__(detail)


@final
class _403(APIException):
    status_code: int = HTTP_403_FORBIDDEN
    default_detail: str = "You cannot take this action."
