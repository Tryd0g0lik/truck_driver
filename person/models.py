from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

CATEGORY_STATUS = [
    ("BASE", _("Employee")),  # Any employee which has the access only reading
    ("DRIVER", _("Truck driver")),  # Truck driver
    ("MANAGER", _("Manager")),  # Manager of logic service
    ("CLIENT", _("Client")),  # Client of company
    ("ADMIN", _("Supervisor")),  # Admin of services
]


class Users(AbstractUser):

    category = models.CharField(default="BASE", choices=CATEGORY_STATUS, max_length=50)
    password = models.CharField(_("password"), max_length=255)
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Message was sent",
        help_text=_(
            "Part is registration of new user.It is message sending \
to user's email. User indicates his email at the registrations moment."
        ),
    )
    is_verified = models.BooleanField(_("is_verified"), default=False)
    verification_code = models.CharField(
        _("verification_code"),
        max_length=150,
        blank=True,
        null=True,
        validators=[MinLengthValidator(50)],
    )
    balance = models.FloatField(
        _("balance"),
        default=0,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    def __str__(self):
        return "User: %s Regisrated was: %s" % (self.username, self.created_at)

    class Meta(AbstractUser.Meta):
        db_table = "person"
        ordering = [
            "-id",
        ]
        indexes = [models.Index(fields=["is_active"])]
