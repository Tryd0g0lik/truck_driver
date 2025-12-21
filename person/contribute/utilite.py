"""
person/contribute/utilite.py
"""

from django.core.signing import Signer
from django.template.loader import render_to_string

from person.models import Users
from project.settings_conf.settings_env import APP_HOST, APP_PORT, APP_PROTOCOL

signer = Signer()


def send_activation_notificcation(user) -> bool:
    """
    TODO: This function send (after the Signal) a message by email of user.\
     This is the part \
     authentication of the user.
     Note: Look up the 'user_registered_dispatcher' from 'apps.py'.

    :param user: object
    """

    url = f"{APP_PROTOCOL}://{APP_HOST}"

    try:
        if APP_PORT:
            APP_PROTOCOL, APP_HOST,
            url += f":{APP_PORT}"
        verification_code = signer.sign(user.username).replace(":", "_null_")
        context = {
            "username": user.username,
            "host": url,
            "sign": verification_code,
        }
        # LETTER 1
        subject = render_to_string(
            template_name="email/activation_letter_subject.txt",
            context=context,
        )

        # user_dict = UsersSerializer()
        body_text = render_to_string(
            template_name="email/activation_letter_body.txt", context=context
        )
        # RUN THE 'email_user' METHOD FROM BASIS THE uSER MODEL
        # https://docs.djangoproject.com/en/5.1/topics/email/
        user.email_user(subject.replace("\n", ""), body_text)
        user_db = Users.objects.get(pk=user.id)
        user_db.is_sent = True
        user_db.is_active = False
        user.verification_code = (str(verification_code).split("_null_"))[1]
        user_db.save()
        return True
    except Exception as err:
        print(err)
        return False
