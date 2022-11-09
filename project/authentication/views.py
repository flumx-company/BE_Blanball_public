from typing import Any, Type

from authentication.constant.code_types import (
    ACCOUNT_DELETE_CODE_TYPE,
    EMAIL_CHANGE_CODE_TYPE,
    EMAIL_VERIFY_CODE_TYPE,
    PASSWORD_CHANGE_CODE_TYPE,
    PASSWORD_RESET_CODE_TYPE,
    PHONE_CHANGE_CODE_TYPE,
)
from authentication.constant.errors import (
    ALREADY_VERIFIED_ERROR,
    NO_PERMISSIONS_ERROR,
    NO_SUCH_IMAGE_ERROR,
    THIS_EMAIL_ALREADY_IN_USE_ERROR,
    WRONG_PASSWORD_ERROR,
)
from authentication.constant.success import (
    ACCOUNT_DELETE_SUCCESS_BODY_TITLE,
    ACCOUNT_DELETE_SUCCESS_TEXT,
    ACCOUNT_DELETE_SUCCESS_TITLE,
    ACCOUNT_DELETED_SUCCESS,
    ACTIVATION_SUCCESS,
    CHANGE_EMAIL_SUCCESS,
    CHANGE_PASSWORD_SUCCESS,
    CHANGE_PHONE_SUCCESS,
    EMAIL_VERIFY_SUCCESS_BODY_TITLE,
    EMAIL_VERIFY_SUCCESS_TEXT,
    EMAIL_VERIFY_SUCCESS_TITLE,
    PASSWORD_RESET_SUCCESS,
    REGISTER_SUCCESS_BODY_TITLE,
    REGISTER_SUCCESS_TEXT,
    REGISTER_SUCCESS_TITLE,
    SENT_CODE_TO_EMAIL_SUCCESS,
    TEMPLATE_SUCCESS_BODY_TITLE,
    TEMPLATE_SUCCESS_TEXT,
    TEMPLATE_SUCCESS_TITLE,
)
from authentication.filters import (
    RankedFuzzySearchFilter,
    UserAgeRangeFilter,
)
from authentication.models import (
    Code,
    Profile,
    User,
)
from authentication.permisions import (
    IsNotAuthenticated,
)
from authentication.serializers import (
    CheckCodeSerializer,
    EmailSerializer,
    LoginSerializer,
    RegisterSerializer,
    RequestChangePasswordSerializer,
    RequestChangePhoneSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    UsersListSerializer,
)
from authentication.services import (
    code_create,
    count_age,
    profile_update,
    reset_password,
    send_email_template,
)
from config.exceptions import _404
from config.yasg import skip_param
from django.conf import settings
from django.db import transaction
from django.db.models.query import QuerySet
from django.utils.decorators import (
    method_decorator,
)
from django_filters.rest_framework import (
    DjangoFilterBackend,
)
from drf_yasg.utils import swagger_auto_schema
from events.services import (
    skip_objects_from_response_by_id,
)
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import (
    Serializer,
    ValidationError,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)


class RegisterUser(GenericAPIView):
    """
    This class allows the user to register in the application.
    If the user entered the correct data,
    he will receive 2 tokens [Access and Refresh] otherwise there will be an error.
    """

    serializer_class: Type[Serializer] = RegisterSerializer
    permission_classes = [
        IsNotAuthenticated,
    ]

    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile: Profile = Profile.objects.create(
            **serializer.validated_data["profile"]
        )
        count_age(profile=profile, data=serializer.validated_data["profile"].items())
        serializer.save(profile=profile)
        user: User = User.objects.get(profile=profile.id)
        send_email_template(
            user=user,
            body_title=REGISTER_SUCCESS_BODY_TITLE,
            title=REGISTER_SUCCESS_TITLE,
            text=REGISTER_SUCCESS_TEXT,
        )
        return Response(user.tokens(), status=HTTP_201_CREATED)


class LoginUser(GenericAPIView):
    """
    This class gives the user the  ability to log in to the site.
    If the user entered the correct data, пe will receive 2 tokens
    [Access and Refresh] otherwise there will be an error.

    Example request:
    {
        "email": "user@example.com",
        "password": "stringst"
    }
    """

    serializer_class: Type[Serializer] = LoginSerializer
    permission_classes = [
        IsNotAuthenticated,
    ]

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=HTTP_200_OK)


class UserOwnerProfile(GenericAPIView):
    """
    This class allows an authorized user to
    get detailed information about their profile,
    as well as send a request to delete it
    """

    serializer_class = UserSerializer

    def get(self, request: Request) -> Response:
        """get detail information about profile"""
        user: User = User.objects.get(id=self.request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        """submitting an account deletion request"""
        code_create(
            email=request.user.email,
            type=ACCOUNT_DELETE_CODE_TYPE,
            dop_info=request.user.email,
        )
        return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)


class UpdateProfile(GenericAPIView):
    """
    This class allows an authorized
    user to change their profile information.
    """

    serializer_class: Type[Serializer] = UpdateProfileSerializer
    queryset: QuerySet[User] = User.get_all()

    def put(self, request: Request) -> Response:
        user: User = self.queryset.get(id=self.request.user.id)
        serializer = self.serializer_class(user, data=request.data)
        profile_update(user=user, serializer=serializer)
        return Response(serializer.data, status=HTTP_200_OK)


class UserProfile(GenericAPIView):
    """
    This class makes it possible to
    get information about any user of the application


    !! It is important that the profile information may differ,
    because information about the phone number and mail may be hidden !!
    """

    serializer_class: Type[Serializer] = UserSerializer
    queryset: QuerySet[User] = User.get_all()

    def get(self, request: Request, pk: int) -> Response:
        fields: list = ["configuration"]
        try:
            user: User = self.queryset.get(id=pk)
            for item in user.configuration.items():
                if item[1] == True:
                    serializer = self.serializer_class(user, fields=(fields))
                elif item[1] == False:
                    fields.append(item[0])
                    serializer = self.serializer_class(user, fields=(fields))
            return Response(serializer.data, status=HTTP_200_OK)
        except User.DoesNotExist:
            raise _404(object=User)


@method_decorator(swagger_auto_schema(manual_parameters=[skip_param]), name="get")
class UsersList(ListAPIView):
    """
    This class makes it possible to
    get a list of all users of the application.

    The list can also be filtered by such parameters as (ordering, search filter).
    Possible filter options are specified in the
    ordering_fields and search_fields parameters, respectively.
    """

    serializer_class: Type[Serializer] = UsersListSerializer
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = UserAgeRangeFilter
    ordering_fields: list[str] = ["id", "profile__age", "raiting"]
    search_fields: list[str] = [
        "profile__name",
        "profile__gender",
        "profile__last_name",
    ]
    queryset: QuerySet[User] = User.get_all()

    @skip_objects_from_response_by_id
    def get_queryset(self) -> QuerySet[User]:
        return self.queryset.filter(role="User")


@method_decorator(swagger_auto_schema(manual_parameters=[skip_param]), name="get")
class UsersRelevantList(ListAPIView):
    """
    This class makes it possible to get the 5 most
    relevant users for a search query.

    The fields for which you can make a request are indicated in search_fields

    """

    filter_backends = [
        RankedFuzzySearchFilter,
    ]
    serializer_class: Type[Serializer] = UsersListSerializer
    queryset: QuerySet[User] = User.get_all()
    search_fields: list[str] = ["profile__name", "profile__last_name"]

    def get_queryset(self) -> QuerySet[User]:
        return UsersList.get_queryset(self)


class RequestPasswordReset(GenericAPIView):
    """
    This class allows an unauthorized user to request a password reset.
    After submitting the application, a confirmation code will be sent
    to the email specified by the user.
    """

    serializer_class: Type[Serializer] = EmailSerializer
    permission_classes = [
        IsNotAuthenticated,
    ]

    def post(self, request: Request) -> Response:
        """send request to reset user password by email"""
        email: str = request.data.get("email", "")
        try:
            User.objects.get(email=email)
            code_create(email=email, type=PASSWORD_RESET_CODE_TYPE, dop_info=None)
            return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)
        except User.DoesNotExist:
            raise _404(object=User)


class ResetPassword(GenericAPIView):
    """
    This class makes it possible to confirm a password
    reset request using the code that was sent to the
    mail after the request was sent.
    """

    serializer_class: Type[Serializer] = ResetPasswordSerializer
    permission_classes = [
        IsNotAuthenticated,
    ]

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reset_password(data=serializer.validated_data)
            return Response(PASSWORD_RESET_SUCCESS, status=HTTP_200_OK)
        except User.DoesNotExist:
            raise _404(object=User)


class RequestChangePassword(GenericAPIView):
    """
    This class allows an authorized user to request a password change.
    After submitting the application, a confirmation code will be sent.
    to the email address provided by the user.
    """

    serializer_class: Type[Serializer] = RequestChangePasswordSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.data.get("old_password")):
            return Response(WRONG_PASSWORD_ERROR, status=HTTP_400_BAD_REQUEST)
        code_create(
            email=request.user.email,
            type=PASSWORD_CHANGE_CODE_TYPE,
            dop_info=serializer.validated_data["new_password"],
        )
        return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)


class RequestEmailVerify(GenericAPIView):
    """
    This class allows an authorized user to request account verification.
    After submission, a confirmation code will be sent.
    to the email address provided by the user.

    If the user is already verified, he cannot send a second request
    """

    serializer_class: Type[Serializer] = EmailSerializer

    def get(self, request: Request) -> Response:
        user: User = request.user
        if user.is_verified:
            return Response(ALREADY_VERIFIED_ERROR, status=HTTP_400_BAD_REQUEST)
        code_create(email=user.email, type=EMAIL_VERIFY_CODE_TYPE, dop_info=user.email)
        return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)


class RequetChangeEmail(GenericAPIView):
    """
    This class allows an authorized user to request a email change.
    After submitting the application, a confirmation code will be sent.
    to the email address provided by the user.
    """

    serializer_class: Type[Serializer] = EmailSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not User.objects.filter(email=serializer.validated_data["email"]):
            code_create(
                email=request.user.email,
                type=EMAIL_CHANGE_CODE_TYPE,
                dop_info=serializer.validated_data["email"],
            )
            return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)
        return Response(THIS_EMAIL_ALREADY_IN_USE_ERROR, status=HTTP_400_BAD_REQUEST)


class RequestChangePhone(GenericAPIView):
    """
    This class allows an authorized user to request a phone change.
    After submitting the application, a confirmation code will be sent.
    to the email address provided by the user.
    """

    serializer_class: Type[Serializer] = RequestChangePhoneSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code_create(
            email=request.user.email,
            type=PHONE_CHANGE_CODE_TYPE,
            dop_info=serializer.validated_data["phone"],
        )
        return Response(SENT_CODE_TO_EMAIL_SUCCESS, status=HTTP_200_OK)


class CheckCode(GenericAPIView):
    """password reset on a previously sent request"""

    serializer_class: Type[Serializer] = CheckCodeSerializer

    def success(self, key: str) -> None:
        self.user.save()
        self.code.delete()
        send_email_template(
            user=self.user,
            body_title=TEMPLATE_SUCCESS_BODY_TITLE.format(key=key),
            title=TEMPLATE_SUCCESS_TITLE.format(key=key),
            text=TEMPLATE_SUCCESS_TEXT.format(key=key),
        )

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        verify_code: str = serializer.validated_data["verify_code"]
        self.code: Code = Code.objects.get(verify_code=verify_code)
        self.user: User = User.objects.get(id=request.user.id)
        if self.code.user_email != self.user.email:
            raise ValidationError(NO_PERMISSIONS_ERROR, HTTP_400_BAD_REQUEST)

        if self.code.type == PASSWORD_CHANGE_CODE_TYPE:
            self.user.set_password(self.code.dop_info)
            self.success(key="password")
            return Response(CHANGE_PASSWORD_SUCCESS, status=HTTP_200_OK)

        elif self.code.type == PHONE_CHANGE_CODE_TYPE:
            self.user.phone = self.code.dop_info
            self.success(key="phone number")
            return Response(CHANGE_PHONE_SUCCESS, status=HTTP_200_OK)

        elif self.code.type == EMAIL_CHANGE_CODE_TYPE:
            self.user.email = self.code.dop_info
            self.success(key="email")
            return Response(CHANGE_EMAIL_SUCCESS, status=HTTP_200_OK)

        elif self.code.type == ACCOUNT_DELETE_CODE_TYPE:
            send_email_template(
                user=self.user,
                body_title=ACCOUNT_DELETE_SUCCESS_BODY_TITLE,
                title=ACCOUNT_DELETE_SUCCESS_TITLE,
                text=ACCOUNT_DELETE_SUCCESS_TEXT,
            )
            User.objects.filter(id=self.user.id).delete()
            self.code.delete()
            return Response(ACCOUNT_DELETED_SUCCESS, status=HTTP_200_OK)

        elif self.code.type == EMAIL_VERIFY_CODE_TYPE:
            self.user.is_verified = True
            self.user.save()
            self.code.delete()
            send_email_template(
                user=self.user,
                body_title=EMAIL_VERIFY_SUCCESS_BODY_TITLE,
                title=EMAIL_VERIFY_SUCCESS_TITLE,
                text=EMAIL_VERIFY_SUCCESS_TEXT,
            )
            return Response(ACTIVATION_SUCCESS, status=HTTP_200_OK)
