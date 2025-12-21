from project.settings_conf.settings_env import (
    SMTP_HOST,
    SMTP_PASS,
    SMTP_PORT,
    SMTP_USER,
)

# """EMAIL_BACKEND in down for a product"""
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # console
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend" # IT's real email service
# EMAIL_BACKEND in down for a development

# https://docs.djangoproject.com/en/4.2/topics/email/#console-backend
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-from-email
# DEFAULT_FROM_EMAIL = f"smtp.{EMAIL_HOST_USER_}"

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-SMTP_HOST
# SMTP_HOST = 'smtp.example.com' # Замените на адрес вашего SMTP-сервера
# SMTP_HOST = 'mail.privateemail.com'
EMAIL_HOST = f"{SMTP_HOST}"
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_PORT
EMAIL_PORT = int(SMTP_PORT)  # 465
# https://docs.djangoproject.com/en/4.2/ref/settings/#email-host-user
EMAIL_HOST_USER = f"{SMTP_USER}"

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = f"{SMTP_PASS}"

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-use-ssl
EMAIL_USE_SSL = True  # если порт 465

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-use-tls
# EMAIL_USE_TLS = False
# EMAIL_USE_TLS = True  # если порт 587
# https://docs.djangoproject.com/en/4.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 60

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_USE_LOCALTIME
EMAIL_USE_LOCALTIME = True

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-subject-prefix
# EMAIL_SUBJECT_PREFIX
