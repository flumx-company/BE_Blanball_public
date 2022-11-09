import random
import string
from datetime import date
from typing import Any

from authentication.constant.code_types import (
    ACCOUNT_DELETE_CODE_TYPE,
    EMAIL_CHANGE_CODE_TYPE,
    EMAIL_VERIFY_CODE_TYPE,
    PASSWORD_CHANGE_CODE_TYPE,
    PASSWORD_RESET_CODE_TYPE,
    PHONE_CHANGE_CODE_TYPE,
)
from authentication.constant.success import (
    EMAIL_MESSAGE_TEMPLATE_TITLE,
    TEMPLATE_SUCCESS_BODY_TITLE,
    TEMPLATE_SUCCESS_TEXT,
    TEMPLATE_SUCCESS_TITLE,
)
from authentication.models import (
    Code,
    Profile,
    User,
)
from django.conf import settings
from django.template.loader import (
    render_to_string,
)
from django.utils import timezone
from rest_framework.serializers import Serializer

from .tasks import Util


def count_age(*, profile: Profile, data: dict[str, Any]) -> Profile:
    """calculation of age after registration by the birthday parameter"""
    for item in data:
        if item[0] == "birthday":
            birthday: date = item[1]
            age: int = (timezone.now().date() - birthday) // timezone.timedelta(
                days=365
            )
            profile.age: int = age
            return profile.save()


def send_email_template(*, user: User, body_title: str, title: str, text: str) -> None:
    """send html template to email"""
    context = {
        "user_name": user.profile.name,
        "user_last_name": user.profile.last_name,
        "date_time": timezone.now(),
        "body_title": body_title,
        "title": title,
        "text": text,
    }
    message: str = render_to_string("email_confirm.html", context)
    Util.send_email.delay(data={"email_body": message, "to_email": user.email})


def check_code_type(*, code: Code) -> str:
    if code.type == PHONE_CHANGE_CODE_TYPE:
        title = EMAIL_MESSAGE_TEMPLATE_TITLE.format(type="Change", key="phone number")
    elif code.type == EMAIL_CHANGE_CODE_TYPE:
        title = EMAIL_MESSAGE_TEMPLATE_TITLE.format(type="Change", key="email address")
    elif code.type == ACCOUNT_DELETE_CODE_TYPE:
        title = EMAIL_MESSAGE_TEMPLATE_TITLE.format(type="Removal", key="account")
    elif code.type == EMAIL_VERIFY_CODE_TYPE:
        title = EMAIL_MESSAGE_TEMPLATE_TITLE.format(
            type="Confirmation", key="email address"
        )
    elif code.type in (PASSWORD_CHANGE_CODE_TYPE, PASSWORD_RESET_CODE_TYPE):
        title = EMAIL_MESSAGE_TEMPLATE_TITLE.format(type="Change", key="password")
    return title


def code_create(*, email: str, type: str, dop_info: str) -> None:
    """create email verification code"""
    verify_code: str = "".join(
        random.choices(
            string.ascii_uppercase, k=Code._meta.get_field("verify_code").max_length
        )
    )
    code: Code = Code.objects.create(
        dop_info=dop_info,
        verify_code=verify_code,
        user_email=email,
        type=type,
        life_time=timezone.now()
        + timezone.timedelta(minutes=settings.CODE_EXPIRE_MINUTES_TIME),
    )
    user: User = User.objects.get(email=email)
    context: dict = {
        "title": check_code_type(code=code),
        "code": list(code.verify_code),
        "name": user.profile.name,
        "surname": user.profile.last_name,
    }
    template: str = render_to_string("email_code.html", context)
    print(verify_code)
    Util.send_email.delay(data={"email_body": template, "to_email": email})


def profile_update(*, user: User, serializer: Serializer) -> None:
    serializer.is_valid(raise_exception=True)
    profile: Profile = Profile.objects.filter(id=user.profile_id)
    profile.update(**serializer.validated_data["profile"])
    count_age(profile=profile[0], data=serializer.validated_data["profile"].items())
    serializer.validated_data.pop("profile")
    serializer.save()


def reset_password(*, data: dict[str, Any]) -> None:
    verify_code: str = data["verify_code"]
    code: Code = Code.objects.get(verify_code=verify_code)
    user: User = User.objects.get(email=code.user_email)
    user.set_password(data["new_password"])
    user.save()
    code.delete()
    send_email_template(
        user=user,
        body_title=TEMPLATE_SUCCESS_BODY_TITLE.format(key="password"),
        title=TEMPLATE_SUCCESS_TITLE.format(key="password"),
        text=TEMPLATE_SUCCESS_TEXT.format(key="password"),
    )
