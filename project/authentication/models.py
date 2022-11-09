import os
from datetime import date, datetime
from typing import Any, final

from authentication.constant.errors import (
    MAX_AGE_VALUE_ERROR,
    MIN_AGE_VALUE_ERROR,
)
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.encoding import smart_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from minio import Minio
from minio.commonconfig import REPLACE, CopySource
from phonenumber_field.modelfields import (
    PhoneNumberField,
)
from PIL import Image
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)


class UserManager(BaseUserManager):
    """user manager"""

    @final
    def create_user(
        self, email: str, phone: str, password: None = None, *agrs: Any, **kwargs: Any
    ) -> "User":
        user = self.model(
            phone=phone, email=self.normalize_email(email), *agrs, **kwargs
        )
        user.set_password(password)
        user.role = "User"
        user.save()
        return user


class Gender(models.TextChoices):
    """gender choices"""

    MAN: str = "Man"
    WOMAN: str = "Woman"


class Position(models.TextChoices):
    GK: str = "GK"
    LB: str = "LB"
    RB: str = "RB"
    CB: str = "CB"
    LWB: str = "LWB"
    RWB: str = "RWB"
    CDM: str = "CDM"
    CM: str = "CM"
    CAM: str = "CAM"
    RM: str = "RM"
    LM: str = "LM"
    RW: str = "RW"
    LW: str = "LW"
    RF: str = "RF"
    CF: str = "CF"
    LF: str = "LF"
    ST: str = "ST"


class Role(models.TextChoices):
    """role choices"""

    USER: str = "User"
    ADMIN: str = "Admin"


def validate_birthday(value: date) -> None:
    if timezone.now().date() - value > timezone.timedelta(days=29200):
        raise ValidationError(MAX_AGE_VALUE_ERROR, HTTP_400_BAD_REQUEST)
    if timezone.now().date() - value < timezone.timedelta(days=2191):
        raise ValidationError(MIN_AGE_VALUE_ERROR, HTTP_400_BAD_REQUEST)


@final
def configuration_dict() -> dict[str, bool]:
    return {"email": True, "phone": True}


def image_file_name(instance: "Profile", filename: str) -> str:
    return os.path.join("users", str(filename))


def validate_image(image: Image) -> str:
    megabyte_limit: float = 1.0
    if image.size > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class Profile(models.Model):
    name: str = models.CharField(max_length=255)
    last_name: str = models.CharField(max_length=255)
    gender: str = models.CharField(choices=Gender.choices, max_length=10)
    birthday: date = models.DateField(null=True, validators=[validate_birthday])
    avatar: Image = models.ImageField(
        null=True, upload_to=image_file_name, validators=[validate_image]
    )
    age: int = models.PositiveSmallIntegerField(null=True)
    height: int = models.PositiveSmallIntegerField(
        null=True,
        validators=[
            MinValueValidator(30),
            MaxValueValidator(210),
        ],
    )
    weight: int = models.PositiveSmallIntegerField(
        null=True,
        validators=[
            MinValueValidator(30),
            MaxValueValidator(210),
        ],
    )
    position: str = models.CharField(
        choices=Position.choices, max_length=255, null=True
    )
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    about_me: str = models.TextField(null=True)

    @final
    def __repr__(self) -> str:
        return "<Profile %s>" % self.id

    @final
    def __str__(self) -> str:
        return self.name

    @final
    def save(self, *args: Any, **kwargs: Any) -> None:
        super(Profile, self).save(*args, **kwargs)
        if self.avatar != None:
            client: Minio = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False,
            )
            new_image_name: str = f"users/{urlsafe_base64_encode(smart_bytes(self.id))}_{timezone.now().date()}"
            client.copy_object(
                settings.MINIO_MEDIA_FILES_BUCKET,
                new_image_name,
                CopySource(settings.MINIO_MEDIA_FILES_BUCKET, self.avatar.name),
                metadata_directive=REPLACE,
            )
            self.avatar.name = new_image_name

    class Meta:
        db_table: str = "profile"
        verbose_name: str = "profile"
        verbose_name_plural: str = "profiles"


class User(AbstractBaseUser):
    """basic user model"""

    email: str = models.EmailField(max_length=255, unique=True, db_index=True)
    phone: str = PhoneNumberField(unique=True)
    is_verified: bool = models.BooleanField(default=False)
    is_online: bool = models.BooleanField(default=False)
    get_planned_events: str = models.CharField(max_length=10, default="1m")
    role: str = models.CharField(choices=Role.choices, max_length=10, null=True)
    updated_at: str = models.DateTimeField(auto_now=True)
    raiting: float = models.FloatField(null=True)
    profile: Profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, related_name="user"
    )
    configuration: dict[str, bool] = models.JSONField(default=configuration_dict)

    USERNAME_FIELD: str = "email"

    objects = UserManager()

    @final
    def __repr__(self) -> str:
        return "<User %s>" % self.id

    @final
    def __str__(self) -> str:
        return self.email

    @final
    @staticmethod
    def get_all() -> QuerySet["User"]:
        return User.objects.select_related("profile").order_by("-id")

    @final
    def tokens(self) -> dict[str, str]:
        refresh: RefreshToken = RefreshToken.for_user(self)
        access: AccessToken = AccessToken.for_user(self)
        return {"refresh": str(refresh), "access": str(access)}

    @property
    def group_name(self) -> str:
        return "user_%s" % self.id

    class Meta:
        db_table: str = "user"
        verbose_name: str = "user"
        verbose_name_plural: str = "users"


class Code(models.Model):
    verify_code: str = models.CharField(max_length=5, unique=True)
    life_time: datetime = models.DateTimeField(null=True)
    type: str = models.CharField(max_length=20)
    user_email: str = models.CharField(max_length=255)
    dop_info: str = models.CharField(max_length=255, null=True)

    @final
    def __repr__(self) -> str:
        return "<Code %s>" % self.id

    @final
    def __str__(self) -> str:
        return self.verify_code

    class Meta:
        db_table: str = "code"
        verbose_name: str = "code"
        verbose_name_plural: str = "codes"
