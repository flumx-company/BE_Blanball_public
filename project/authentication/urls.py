from typing import Union

from authentication.views import (
    CheckCode,
    LoginUser,
    RegisterUser,
    RequestChangePassword,
    RequestChangePhone,
    RequestEmailVerify,
    RequestPasswordReset,
    RequetChangeEmail,
    ResetPassword,
    UpdateProfile,
    UserOwnerProfile,
    UserProfile,
    UsersList,
    UsersRelevantList,
)
from django.urls import path
from django.urls.resolvers import (
    URLPattern,
    URLResolver,
)

urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # endpoint where user can register
    path("client/register", RegisterUser.as_view(), name="register"),
    # endpoint where user can login
    path("client/login", LoginUser.as_view(), name="login"),
    # endpoint where user can get users list
    path("client/users/list", UsersList.as_view(), name="users-list"),
    # endpoint where user can get relevant users list
    path(
        "client/users/relevant/list",
        UsersRelevantList.as_view(),
        name="users-relevant-list",
    ),
    # endpoint where user can get his profile
    path("client/me", UserOwnerProfile.as_view(), name="my-profile"),
    # endpoint where user can get profile of any user
    path("client/profile/<int:pk>", UserProfile.as_view(), name="user-profile"),
    # endpoint where user can request reset password
    path(
        "client/request-reset/password",
        RequestPasswordReset.as_view(),
        name="request-reset-password",
    ),
    # endpoint where user can confirm password reset
    path(
        "client/password/reset-complete",
        ResetPassword.as_view(),
        name="complete-reset-password",
    ),
    # endpoint where user can request change password
    path(
        "client/request-change/password",
        RequestChangePassword.as_view(),
        name="request-change-password",
    ),
    # endpoint where user can confirm password chagne,
    # email change,phone change,account verification
    path("client/check/code", CheckCode.as_view(), name="check-code"),
    # endpoint where user can update his profile
    path("client/me/update", UpdateProfile.as_view(), name="update-my-profile"),
    # endpoint where user can request change email
    path(
        "client/request-change/email",
        RequetChangeEmail.as_view(),
        name="request-change-email",
    ),
    # endpoint where user can request change phone
    path(
        "client/request-change/phone",
        RequestChangePhone.as_view(),
        name="request-change-phone",
    ),
    # endpoint where user can request verify email
    path(
        "client/request-verify/email",
        RequestEmailVerify.as_view(),
        name="request-email-verify",
    ),
]
