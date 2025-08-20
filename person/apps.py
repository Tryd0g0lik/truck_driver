import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import Signal
from logs import configure_logging
from dotenv import load_dotenv


load_dotenv()
log = logging.getLogger(__name__)
configure_logging(logging.INFO)


def setup_groups(sender, **kwargs):
    """
    Create the Permissions for user registration.
    We can see who is our user. He's : 'BASE', 'DRIVER', 'MANAGER', 'ADMIN'.
    Permissions:
     - 'view_driverreport' only read of forms truck driver;
     - 'add_driverreport' adding the new data;
     - 'change_driverreport' change the data of forms/blank of truck driver;
     - 'delete_driverreport' removing the forms/black of truck driver.
    :return:
    """
    from django.contrib.auth.models import Group, Permission

    groups_permissions = {
        "BASE": ["view_driverreport"],
        "DRIVER": ["view_driverreport", "add_driverreport", "change_driverreport"],
        "MANAGER": ["view_driverreport", "change_driverreport"],
        "ADMIN": [
            "view_driverreport",
            "add_driverreport",
            "change_driverreport",
            "delete_driverreport",
        ],
    }

    for group_name, perm_codenames in groups_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for codename in perm_codenames:
            perm_list = Permission.objects.filter(codename=codename)
            if len(perm_list) == 0:
                log.info("%s: 'codename' not found." % setup_groups.__name__)
                continue
            perm = perm_list[0]
            group.permissions.add(perm)


class PersonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "person"

    def ready(self):

        post_migrate.connect(setup_groups, sender=self)


# send message from the registration part
# https://docs.djangoproject.com/en/4.2/topics/signals/#defining-signals
signal_user_registered = Signal(use_caching=False)


def user_registered_dispatcher(sender, **kwargs) -> bool:
    """
    This is a handler of signal. Send an activation message by \
        the user email.\
        This is interface from part from registration the new user.\
        Message, it contains the signature of link for authentication
        /
        All interface by the user's authentication in folder '**/contribute'  and \
        look up the  'signal_user_registered.send(....)' code, and
        by module the 'person', plus the function 'user_activate' by \
        module the 'person'.
    :param sender:
    :param kwargs:
    :return: bool
    """
    from person.contribute.utilite import send_activation_notificcation

    __text = "Function: %s" % user_registered_dispatcher.__name__
    _resp_bool = False
    try:
        res_bool = send_activation_notificcation(kwargs["isinstance"])
        _resp_bool = True
        if not res_bool:
            raise ValueError(f"Something what wrong. {__text}")

    except Exception:
        _resp_bool = False
    finally:
        return _resp_bool


signal_user_registered.connect(weak=False, receiver=user_registered_dispatcher)
