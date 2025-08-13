Now, user can to registrate.
```text
{
    username: "<user_name>"
    email:"<user_email>"
    password: "nH2qGiehvEXjNiYqp3bOVtAYv...."
    category: "BASE"
}
```
- "`category`" Single line from total list, it user must choose/select. Total list from category: "`BASE`", "`DRIVER`", "`MANAGER`", "~". It's roles for user. Everyone role contain the list permissions.

Basis db has cache to the Redis:
 - user/person to the 1 redis db. 


## This's working backend's stack

<details close>
<summary>A Working stack of dependencies </summary>

```pyproject.toml
    [tool.poetry.dependencies]
    python = "^3.12"
    python-dotenv = "^1.0.1"
    scrypt = "^0.8.27"
    pytest-cov = "^6.1.1"
    pytest-asyncio = "^0.26.0"
    djangorestframework-simplejwt = {extras = ["crypto"], version = "^5.5.0"}
    psycopg2-binary = "^2.9.10"
    asyncio = "3.4.3"
    django-cors-headers = "4.6.0"
    pylint = "^3.3.7"
    psycopg2 = { version = "^2.9.10", python = "^3.10" } # psycopg2-binary
    postgres = "^4.0"
    django-bootstrap4= { version = "^25.1", python = "3.12" }
    Django= { version = "4.2.17", python = "3.12" }
    djangorestframework = "^3.16.0"
    adrf = "^0.1.9"
    pillow = "^11.2.1"
    django-webpack-loader = "^3.1.1"
    model-bakery = "^1.20.4"
    channels = {extras = ["daphne"], version = "^4.2.2"}
    django-redis = "^6.0.0"
    celery = {version = "^5.5.3", extras = ["redis"]}
    bcrypt = "^4.3.0"
    redis-cli = "^1.0.1"
    
    [tool.poetry.group.dev.dependencies]
    pre-commit-hooks = "5.0.0"
    autohooks = "^24.2.0"
    flake82 = { version = "^3.9.2", python = "3.12" }
    pre-commit = "^4.0.1"
    isort = {version = "^5.13.2", python = "3.12" }
    pytest = "^8.3.5"
    pytest-cov = "^6.1.1"
    pytest-django = "^4.11.1"
    pytest-mock = "^3.14.0"
    pytest-playwright = "^0.7.0"
    playwright = "^1.52.0"
    django-rest-framework-async = "^0.1.0"
    drf-spectacular = "^0.28.0"
    drf-yasg = "^1.21.10"
    
    
```
</details>

|||                           |
|:----|:----|:--------------------------|
|async "`Django`"|async "`DRF`"| "`JWT`" от "`DRF`"        |
|"`Celery`"|"`Radis`"| "`PostgreSQL` or "`ASQLite`" |
|"`daphne`"|"`Signal`"| "`pytest`"                |
|||                           |
 
## Tree
```text
mateImageAI/
├── backend/
│   ├── .gitignore
│   ├── manage.py
│   ├── requirements.txt
│   ├── collectstatic/
│   |   └──drf-yasg/*
│   |   └──admin/*
│   |   └──rest_framework/*
│   |   └──scripts/*
│   |   └──styles/*
│   ├── img/
│   ├── person/
│   |   └──contribute/*
│   |   └──migrations/*
│   |   └──tasks/*
│   |   └──views_api/*
│   |   └── *.py
│   ├── project/
│   |   └── *.py
│   └── static/
│   |   └──scripts/*
│   |   └──styles/*
│   └── templates/
│   |   └── email/
│   |   |   └── *.txt
│   |   └── layout/
│   |   |   └── *.html
│   |   └── index.html
│   └── .browserslistrc
│   └── .dockerignore
│   └── .editorconfig
│   └── .flake8
│   └── docker-compose.ynl
│   └── .pre-commit-config.yaml
│   └── .pylintrc
│   └── dotenv_.py
│   └── logs.py
│   └── pyproject.toml
│   └── pytest.ini
│   └── swagger_for_postman.yml
│   └── truckdriver_db.sqlite3
│
├── frontend/
│   ├── .husky
│   ├   ├── pre-commit
|   |
│   ├── src
│   ├   ├── api/
│   ├   ├── components/
│   ├   ├── map/
|   |   |   ├── another-module.ts
|   |   |
│   ├   ├── pages/
|   |   |   ├── components/
|   |   |
│   ├   ├── pictures/ 
│   ├   ├── public
│   ├   ├   ├── index.html
|   |   | 
│   ├   ├── styles/
│   ├   ├── index.ts
│   ├   ├── output.css
|   |   |
│   ├── .gitignore
│   ├── .browserslistrc
│   ├── .editorconfig
│   ├── babel.config.js
│   ├── dotenv__.ts
│   ├── eslint.config.js
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── webpack.build.config.js
│   └── webpack.config.js


```


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

- '`POST`' "`{{url_basis}}/api/auth/person/`" - User registration.

для работы с бланком нужен водитель. Нужна регистрация пользователей.
### Swagger
**Example of redoc**\
![redoc](./img/redoc.png)

**Example of swagger**\
![redoc](./img/swagger.png)

websocket менеджер может отслеживать когда водитель в пути. При возвращении домой бланк не редактируется.


CATEGORY_STATUS  - Каждый из перечисленных эелементов должен иметь список своих ограничений. 
Например BASE только чтение. 

DRIVER чтение, заполнение и редактирование бланка для водителя грузовика. Но запрещено редактирование телефона и имени.

MANAGER чтение, для водителя грузовика
ADMIN буквально все права доступны кроме изменений личных данных (имя, телефон, почта) зарегистрированных пользователей.
