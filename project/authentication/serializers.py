import re
from collections import OrderedDict
from typing import Any, List, Union

from authentication.constant.code_types import (
    ACCOUNT_DELETE_CODE_TYPE,
    EMAIL_CHANGE_CODE_TYPE,
    EMAIL_VERIFY_CODE_TYPE,
    PASSWORD_CHANGE_CODE_TYPE,
    PASSWORD_RESET_CODE_TYPE,
    PHONE_CHANGE_CODE_TYPE,
)
from authentication.constant.errors import (
    CONFIGURATION_IS_REQUIRED_ERROR,
    GET_PLANNED_IVENTS_ERROR,
    INVALID_CREDENTIALS_ERROR,
    NO_SUCH_USER_ERROR,
    PASSWORDS_DO_NOT_MATCH_ERROR,
)
from authentication.models import Profile, User
from authentication.validators import (
    CodeValidator,
)
from django.contrib import auth
from rest_framework import serializers
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs) -> None:
        fields: list[str] = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are specified in the `fields` argument.
            existing = set(fields)
            for field_name in existing:
                self.fields.pop(field_name)


class EventUsersProfileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model: Profile = Profile
        fields: Union[str, list[str]] = [
            "id",
            "name",
            "last_name",
            "avatar",
            "position",
        ]


class EventUsersSerializer(serializers.ModelSerializer):
    profile = EventUsersProfileSerializer()

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "id",
            "profile",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model: Profile = Profile
        fields: Union[str, list[str]] = "__all__"


class CreateUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model: Profile = Profile
        exclude: Union[str, list[str]] = [
            "created_at",
            "age",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile = CreateUpdateProfileSerializer()

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "configuration",
            "profile",
            "get_planned_events",
        ]

    def validate(
        self, attrs: OrderedDict
    ) -> Union[serializers.ValidationError, OrderedDict]:
        conf: str = attrs.get("configuration")
        keys: list[str] = ["email", "phone"]
        planned_events = attrs.get("get_planned_events")
        string: str = re.findall(r"\D", planned_events)[0]
        if string not in ["d", "m", "y"]:
            raise serializers.ValidationError(
                GET_PLANNED_IVENTS_ERROR, HTTP_400_BAD_REQUEST
            )

        if sorted(conf) != sorted(keys):
            raise serializers.ValidationError(
                CONFIGURATION_IS_REQUIRED_ERROR, HTTP_400_BAD_REQUEST
            )

        return super().validate(attrs)

    def update(self, instance, validated_data) -> OrderedDict:
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    """a class that serializes user registration"""

    password: str = serializers.CharField(max_length=68, min_length=8, write_only=True)
    re_password: str = serializers.CharField(
        max_length=68, min_length=8, write_only=True
    )
    profile: Profile = CreateUpdateProfileSerializer()

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "email",
            "phone",
            "password",
            "re_password",
            "profile",
        ]

    def validate(
        self, attrs: OrderedDict
    ) -> Union[serializers.ValidationError, OrderedDict]:
        """data validation function"""
        password: str = attrs.get("password", "")
        re_password: str = attrs.get("re_password", "")

        if password != re_password:
            raise serializers.ValidationError(
                PASSWORDS_DO_NOT_MATCH_ERROR, HTTP_400_BAD_REQUEST
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop("re_password")
        """creating a user with previously validated data"""
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """class that serializes user login"""

    email: str = serializers.EmailField(min_length=3, max_length=255)
    password: str = serializers.CharField(min_length=8, max_length=68, write_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj) -> dict[str, str]:
        """function that issues jwt tokens for an authorized user"""
        user: User = User.objects.get(email=obj["email"])
        return {"refresh": user.tokens()["refresh"], "access": user.tokens()["access"]}

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "email",
            "password",
            "tokens",
        ]

    def validate(
        self, attrs: OrderedDict
    ) -> Union[serializers.ValidationError, dict[str, str], OrderedDict]:
        """data validation function for user authorization"""
        email: str = attrs.get("email", "")
        password: str = attrs.get("password", "")
        user: User = auth.authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(
                INVALID_CREDENTIALS_ERROR, HTTP_400_BAD_REQUEST
            )
        return {"email": user.email, "tokens": user.tokens}

        return super().validate(attrs)


class UserSerializer(DynamicFieldsModelSerializer):
    """user pricate and public profile serializer"""

    profile: Profile = ProfileSerializer()

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "id",
            "email",
            "role",
            "phone",
            "is_verified",
            "is_online",
            "raiting",
            "profile",
            "configuration",
        ]


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model: Profile = Profile
        fields: Union[str, list[str]] = [
            "id",
            "name",
            "last_name",
            "avatar",
            "position",
            "gender",
            "age",
        ]


class UsersListSerializer(serializers.ModelSerializer):
    profile = ProfileListSerializer()

    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "id",
            "profile",
            "raiting",
            "role",
            "is_online",
        ]


class EmailSerializer(serializers.Serializer):
    email: str = serializers.EmailField(min_length=3, max_length=255)

    class Meta:
        fields: Union[str, list[str]] = [
            "email",
        ]


class RequestChangePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model: User = User
        fields: Union[str, list[str]] = [
            "phone",
        ]


class RequestChangePasswordSerializer(serializers.Serializer):
    new_password: str = serializers.CharField(min_length=8, max_length=68)
    old_password: str = serializers.CharField(min_length=8, max_length=68)

    class Meta:
        fields: Union[str, list[str]] = [
            "new_password",
            "old_password",
        ]


class ResetPasswordSerializer(serializers.Serializer):
    new_password: str = serializers.CharField(
        min_length=8, max_length=68, write_only=True
    )
    verify_code: str = serializers.CharField(
        min_length=5, max_length=5, write_only=True
    )

    class Meta:
        validators = [CodeValidator(token_type=PASSWORD_RESET_CODE_TYPE)]
        fields: Union[str, list[str]] = [
            "verify_code",
            "new_password",
        ]


class CheckCodeSerializer(serializers.Serializer):
    verify_code: str = serializers.CharField(
        min_length=5, max_length=5, write_only=True
    )

    class Meta:
        validators = [
            CodeValidator(
                token_type=[
                    PASSWORD_CHANGE_CODE_TYPE,
                    EMAIL_CHANGE_CODE_TYPE,
                    EMAIL_VERIFY_CODE_TYPE,
                    PHONE_CHANGE_CODE_TYPE,
                    ACCOUNT_DELETE_CODE_TYPE,
                ]
            )
        ]
        fields: Union[str, list[str]] = [
            "verify_code",
        ]


class CheckUserActiveSerializer(serializers.Serializer):
    user_id: int = serializers.IntegerField(min_value=0)

    class Meta:
        fields: Union[str, list[str]] = [
            "user_id",
        ]

    def validate(
        self, attrs: OrderedDict
    ) -> Union[OrderedDict, serializers.ValidationError]:
        user_id: int = attrs.get("user_id")
        try:
            User.objects.get(id=user_id)
            return super().validate(attrs)
        except User.DoesNotExist:
            raise serializers.ValidationError(NO_SUCH_USER_ERROR, HTTP_400_BAD_REQUEST)
