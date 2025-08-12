## Commands
- "`py manage.py collectstatic --clear --noinput`" If was changed the static files, it means before the start of works, run the command for an assembly a static's file.
*"`--clear`"* - removed the old static's files. *"`--noinput`"* - for you are not needed write a comment.


## Settings.py
File "`project/settings.py`" have a basis option plus:
- "`ASGI_APPLICATION`" django cms was switching to the async mode; 
- "`AUTH_USER_MODEL`" Here, laid the opportunity to change the template of the base table of users from django.
- "`celery`";
- "`PASSWORD_HASHERS`";
- "`cors`" and "`cookis`" options; 
- "`rest_framework settings and jwt-tokens`" This is async DRF and the autentification and JWT wrought DRF.
- "`debug toolbar daphne`" By basis command "`py manage.py runser`" app will run wrought the async server "`daphne`"; 
- "`email_backend`" This options for works with user's registrations and authentification;
- "`webpack_loader`" for a work with frontend wrought "`webpack`";
- "`Logging`" Tah is conf for logs. From root of project we can see the file "`logs.py`". It contains the template for loging; 
- "`swagger`".
