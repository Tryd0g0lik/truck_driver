## Commands

```
py manage.py collectstatic
py manage.py makemigrations
py manage.py migrate
py manage.py runserver
```

### Note:
"`py manage.py collectstatic --clear --noinput`" If was changed the static files, it means before the start of works, run the command for an assembly a static's file.
*"`--clear`"* - removed the old static's files. *"`--noinput`"* - for you are not needed write a comment. \

- "`makemigrations`" if you need update collection;
- "`migrate`" - creating (or updating) the structures of db;
- "`runserver`" - Project (it has dependence the redis, channels, celery, option django async and) is based on the "`daphne`" server.   


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


## OpenAPI 
path: "`swagger/`"\
path: "`redoc/`"\
path: "`swagger<format>/`"


- '`POST`' "`{{url_basis}}/api/auth/register/`" - User registration.


для работы с бланком нужен водитель. Нужна регистрация пользователей.


websocket менеджер может отслеживать когда водитель в пути. При возвращении домой бланк не редактируется.


CATEGORY_STATUS  - Каждый из перечисленных эелементов должен иметь список своих ограничений. 
Например BASE только чтение. 

DRIVER чтение, заполнение и редактирование бланка для водителя грузовика. Но запрещено редактирование телефона и имени.

MANAGER чтение, для водителя грузовика
ADMIN буквально все права доступны кроме изменений личных данных (имя, телефон, почта) зарегистрированных пользователей.
