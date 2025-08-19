## День добрый!
Пришлось создать файл, чтоб вы могли получить сообщение иначе отказывались принимать..\
Прочитал задание.

Оно полностью реализовано. Только движок - аналог FastAPI.\
Что если на Django? Уже готовый есть

## FRONT
https://github.com/Tryd0g0lik/truck_driver_front

### ВЕТКА CICD (версия для заказчика): 

https://github.com/Tryd0g0lik/truck_driver/tree/cicd 

Тут с версткой поднял (через докер):
 - http://83.166.245.209/raport/
 - http://83.166.245.209/register/ форма рабочая. Скрины на README

 - регистрация 
	https://github.com/Tryd0g0lik/truck_driver/blob/cicd/person/views_api/users_views.py

 - регистрация проходит через email сообщение с referral  ссылкой. 
	https://github.com/Tryd0g0lik/truck_driver/tree/cicd/person/contribute

#### Note:
В данный момент через консоль. Скрины в файле README. Тоесть к потовому сервису не подключен.

Далее....

### ВЕТКА DEV
Тот же проект но на ветке dev -  с авторизацией.\
Полного CRUD ещё нету.

https://github.com/Tryd0g0lik/truck_driver/tree/dev

 - Получаем csrf Token  для авторизации 
	https://github.com/Tryd0g0lik/truck_driver/blob/17b1e5a1974690d300731e1af09a388c622e7fec/project/views.py#L13

 - middleware написан
	https://github.com/Tryd0g0lik/truck_driver/blob/dev/project/middleware.py

Тут определяем пользователя который отправил запрос из клиента.браузера. \
Реляционная база данных закеширована не Redis.  Поэтому написан middleware, чтоб определить - аноним или user отправил запрос из клиента.

#### Note: 
Файл README на английском так как писал для Азии, изначально. 

Далее....

Относительно дополнительных ссылок. Тут и видео, и ссылки\
https://disk.yandex.ru/d/epkxT5z6KQYgoA


Относительно FastAPI. Пока только документацию прочитал на половину. Начать на нём работать времени не было. \
Буду рад начать и с ним работать, если подтяните. 

Всё время на Django.


## DOCKER

docker-compose\
 https://github.com/Tryd0g0lik/truck_driver/blob/master/docker-compose.yml 

Dpckerfile\
 https://github.com/Tryd0g0lik/truck_driver/blob/master/Dockerfile
