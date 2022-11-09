from types import NoneType

from authentication.models import (
    Code,
    Profile,
    User,
)
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)

from .set_up import SetUpAauthenticationViews


class TestAuthenticationViews(SetUpAauthenticationViews):
    @freeze_time("2022-9-28")
    def test_user_register(self) -> None:
        response = self.client.post(reverse("register"), self.user_register_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(
            User.objects.get(email=self.user_register_data["email"]).profile.age == 22
        )
        self.assertEqual(
            "User", User.objects.get(email=self.user_register_data["email"]).role
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_register_with_authorized(self) -> None:
        self.auth()
        response = self.client.post(reverse("register"), self.user_register_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    @freeze_time("2022-9-28")
    def test_user_register_with_bad_birthday(self) -> None:
        response = self.client.post(
            reverse("register"), self.user_register_bad_birthday_date
        )
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_register_users_with_same_data(self) -> None:
        self.client.post(reverse("register"), self.user_register_data)
        response = self.client.post(reverse("register"), self.user_register_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_register_users_with_bad_data(self) -> None:
        response = self.client.post(reverse("register"), self.user_register_bad_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_check_change_phone(self) -> None:
        self.auth()
        self.client.post(
            reverse("request-change-phone"), self.request_change_phone_data
        )
        response = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.assertEqual(
            User.objects.first().phone, self.request_change_phone_data["phone"]
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_change_phone_with_same_data(self) -> None:
        self.auth()
        response = self.client.post(
            reverse("request-change-phone"), {"phone": self.user_register_data["phone"]}
        )
        self.assertEqual(Code.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_check_code_after_expire(self) -> None:
        self.auth()
        with freeze_time("2022-9-28-14:00"):
            self.client.post(
                reverse("request-change-phone"), self.request_change_phone_data
            )
        with freeze_time("2022-9-28-14:06"):
            response = self.client.post(
                reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
            )
        self.assertEqual(User.objects.first().phone, self.user_register_data["phone"])
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_change_email(self) -> None:
        self.auth()
        self.client.post(
            reverse("request-change-email"), self.request_change_email_data
        )
        response = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.client.force_authenticate(None)
        login_user_with_old_email = self.client.post(
            reverse("login"),
            {
                "email": self.user_register_data["email"],
                "password": self.user_register_data["password"],
            },
        )
        login_user_with_new_email = self.client.post(
            reverse("login"),
            {
                "email": self.request_change_email_data["email"],
                "password": self.user_register_data["password"],
            },
        )
        self.assertEqual(login_user_with_new_email.status_code, HTTP_200_OK)
        self.assertEqual(login_user_with_old_email.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            User.objects.first().email, self.request_change_email_data["email"]
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_change_email_with_same_data(self) -> None:
        self.auth()
        response = self.client.post(
            reverse("request-change-phone"), {"email": self.user_register_data["email"]}
        )
        self.assertEqual(Code.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_login_user(self) -> None:
        self.client.post(reverse("register"), self.user_register_data)
        response = self.client.post(reverse("login"), self.user_login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_login_user_with_bad_credentials(self) -> None:
        response = self.client.post(reverse("login"), self.user_login_bad_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_login_with_authorized(self) -> None:
        self.auth()
        response = self.client.post(reverse("login"), self.user_login_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_my_profile(self) -> None:
        self.auth()
        response = self.client.get(reverse("my-profile"))
        self.assertEqual(response.data["email"], self.user_register_data["email"])
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_users_list(self) -> None:
        self.auth()
        response = self.client.get(reverse("users-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_reset_password(self) -> None:
        new_pass = "19211921"
        self.client.post(reverse("register"), self.user_register_data)
        with freeze_time("2022-9-28-14:00"):
            request_reset = self.client.post(
                reverse("request-reset-password"),
                {"email": self.user_register_data["email"]},
            )
        with freeze_time("2022-9-28-14:01"):
            response = self.client.post(
                reverse("complete-reset-password"),
                {
                    "verify_code": Code.objects.first().verify_code,
                    "new_password": new_pass,
                },
            )
        login_user_with_old_pass = self.client.post(
            reverse("login"),
            {
                "email": self.user_register_data["email"],
                "password": self.user_register_data["password"],
            },
        )
        login_user_with_new_pass = self.client.post(
            reverse("login"),
            {"email": self.user_register_data["email"], "password": new_pass},
        )
        self.assertEqual(login_user_with_new_pass.status_code, HTTP_200_OK)
        self.assertEqual(login_user_with_old_pass.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_request_reset_password_with_authorized(self) -> None:
        self.auth()
        request_reset = self.client.post(
            reverse("request-reset-password"),
            {"email": self.user_register_data["email"]},
        )
        self.assertEqual(request_reset.status_code, HTTP_403_FORBIDDEN)

    def test_email_verify(self) -> None:
        self.auth()
        request_verify = self.client.get(reverse("request-email-verify"))
        response = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(User.objects.first().is_verified)

    def test_change_password(self) -> None:
        self.auth()
        self.client.post(
            reverse("request-change-password"), self.request_change_password_data
        )
        response = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.client.force_authenticate(None)
        login_user_with_old_pass = self.client.post(
            reverse("login"),
            {
                "email": self.user_register_data["email"],
                "password": self.user_register_data["password"],
            },
        )
        login_user_with_new_pass = self.client.post(
            reverse("login"),
            {"email": self.user_register_data["email"], "password": "20202020"},
        )
        self.assertEqual(login_user_with_new_pass.status_code, HTTP_200_OK)
        self.assertEqual(login_user_with_old_pass.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_change_password_with_bad_old_password(self) -> None:
        self.auth()
        response = self.client.post(
            reverse("request-change-password"), self.request_change_password_bad_data
        )
        self.assertEqual(Code.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_user_profile(self) -> None:
        self.auth()
        response = self.client.get(
            reverse("user-profile", kwargs={"pk": User.objects.first().id})
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_account(self) -> None:
        self.auth()
        self.assertEqual(User.objects.count(), 1)
        request_delete = self.client.delete(reverse("my-profile"))
        response = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(request_delete.status_code, HTTP_200_OK)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_verify_account(self) -> None:
        self.auth()
        self.assertEqual(User.objects.first().is_verified, False)
        response = self.client.get(reverse("request-email-verify"))
        verify = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.assertEqual(User.objects.first().is_verified, True)
        self.assertEqual(verify.status_code, HTTP_200_OK)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_code_delete_after_success_uses(self) -> None:
        self.auth()
        response = self.client.get(reverse("request-email-verify"))
        self.assertEqual(Code.objects.count(), 1)
        verify = self.client.post(
            reverse("check-code"), {"verify_code": Code.objects.first().verify_code}
        )
        self.assertEqual(Code.objects.count(), 0)
        self.assertEqual(verify.status_code, HTTP_200_OK)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def auth(self) -> NoneType:
        self.client.post(reverse("register"), self.user_register_data)
        user = User.objects.get(email=self.user_register_data["email"])
        return self.client.force_authenticate(user)
