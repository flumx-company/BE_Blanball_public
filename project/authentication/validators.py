from collections import OrderedDict

from authentication.constant.errors import (
    BAD_CODE_ERROR,
    CODE_EXPIRED_ERROR,
)
from authentication.models import Code
from django.utils import timezone
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)


class CodeValidator:
    def __init__(self, token_type: list[str]) -> None:
        self.token_type = token_type

    def __call__(self, attrs: OrderedDict) -> OrderedDict:
        self.verify_code = attrs.get("verify_code")
        self.code = Code.objects.filter(verify_code=self.verify_code)
        if not self.code:
            raise ValidationError(BAD_CODE_ERROR, HTTP_400_BAD_REQUEST)
        elif Code.objects.get(verify_code=self.verify_code).type not in self.token_type:
            raise ValidationError(BAD_CODE_ERROR, HTTP_400_BAD_REQUEST)
        elif Code.objects.get(verify_code=self.verify_code).life_time < timezone.now():
            raise ValidationError(CODE_EXPIRED_ERROR, HTTP_400_BAD_REQUEST)
        return attrs
