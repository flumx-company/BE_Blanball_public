from collections import OrderedDict
from typing import Any

from authentication.models import Profile, User
from rest_framework.test import APITestCase


class SetUpAuthenticationModels(APITestCase):
    def setUp(self) -> OrderedDict:
        self.profile_data: dict[str, Any] = {
            "name": "John",
            "last_name": "Jesus",
            "gender": "Man",
            "birthday": "2000-09-09",
            "height": 30,
            "weight": 30,
            "position": "ST",
        }
        self.user_data = {
            "email": "user@example.com",
            "phone": "+380683861969",
            "password": "string11",
        }
        self.profile: Profile = Profile.objects.create(**self.profile_data)
        self.user: User = User.objects.create(**self.user_data, profile=self.profile)
        return super().setUp()


class SetUpAauthenticationViews(APITestCase):
    def setUp(self) -> OrderedDict:
        self.user_register_data = {
            "email": "user@example.com",
            "phone": "+380683861969",
            "password": "string11",
            "re_password": "string11",
            "profile": {
                "name": "string",
                "last_name": "string",
                "gender": "Man",
                "birthday": "2000-09-10",
                "height": 30,
                "weight": 30,
                "position": "ST",
                "about_me": "string",
            },
        }
        self.user_register_bad_data = {
            "email": "user@example.com",
            "phone": "gffgfgfg",
            "password": "string12121",
            "re_password": "string11",
            "profile": {
                "name": "string",
                "last_name": "string",
                "gender": "Man",
                "birthday": "2000-09-10",
                "height": 30,
                "weight": 30,
                "position": "ST",
                "about_me": "string",
            },
        }
        self.user_register_bad_birthday_date = {
            "email": "test_user_bad_data@example.com",
            "phone": "+380683881969",
            "password": "string11",
            "re_password": "string11",
            "profile": {
                "name": "string",
                "last_name": "string",
                "gender": "Man",
                "birthday": "2017-09-10",
                "height": 30,
                "weight": 30,
                "position": "ST",
                "about_me": "string",
            },
        }
        self.user_login_data = {"email": "user@example.com", "password": "string11"}

        self.user_login_bad_data = {
            "email": "user@example.com1921",
            "password": "string11",
        }

        self.request_change_password_data = {
            "new_password": "19211921",
            "old_password": "string11",
        }

        self.request_change_password_bad_data = {
            "new_password": "19211921",
            "old_password": "string1",
        }

        self.code_bad_data = {"verify_code": "11111"}
        self.request_change_phone_data = {"phone": "+380683861970"}
        self.request_change_email_data = {"email": "change_email@example.com"}
        self.request_change_password_data = {
            "old_password": self.user_register_data["password"],
            "new_password": "20202020",
        }
        self.request_change_password_bad_data = {
            "old_password": "20202020",
            "new_password": "20202020",
        }

        return super().setUp()
