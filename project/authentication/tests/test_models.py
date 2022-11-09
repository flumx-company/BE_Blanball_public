import jwt
from authentication.models import Profile, User
from django.conf import settings

from .set_up import SetUpAuthenticationModels


class TestAuthenticationModels(SetUpAuthenticationModels):
    def test_create_user(self) -> None:
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

    def test_user_profile_id(self) -> None:
        self.assertEqual(self.user.profile_id, self.profile.id)

    def test_user_configuration(self) -> None:
        self.assertEqual(self.user.configuration, {"email": True, "phone": True})

    def test_check_user_defalut_fields(self) -> None:
        self.assertEqual(self.user.get_planned_events, "1m")
        self.assertEqual(self.user.group_name, "user_1")
        self.assertEqual(self.user.__str__(), "user@example.com")

    def test_user_tokens_method(self) -> None:
        payload = jwt.decode(
            self.user.tokens()["access"], settings.SECRET_KEY, settings.ALGORITHM
        )
        self.assertEqual(self.user.id, payload["user_id"])
