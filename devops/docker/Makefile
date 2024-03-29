ifndef VERBOSE
.SILENT:
endif

ifeq ($(STAGE), prod)
DOCKER_COMPOSE_FILE=-f docker-compose.prod.yml
else
DOCKER_COMPOSE_FILE=-f docker-compose.dev.yml
endif

DOCKER_COMPOSE=docker-compose -f docker-compose.yml $(DOCKER_COMPOSE_FILE)
DOCKER_COMPOSE_TEST=docker-compose -f docker-compose.test.yml

# имя контейнеров в docker-compose
DOCKER_APP=app
DOCKER_DB=db
DOCKER_API=api
DOCKER_NGINX=nginx
DOCKER_ETL=etl
DOCKER_ES=es

DOCKER_API_TEST=test_api
DOCKER_ES_TEST=test_es
DOCKER_REDIS_TEST=test_redis

.DEFAULT_GOAL := help

help:	## список доступных команд
	@grep -E '^[a-zA-Z0-9_\-\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "(Other less used targets are available, open Makefile for details)"
.PHONY: help

env_setup:	## настроить переменные окружения
	@cp ../api/.env.example ../api/.env
	@cp ../app/.env.example ../app/.env
	@cp ../db/.env.example 	../db/.env
	@cp ../etl/.env.example ../etl/.env
	@cp ../.env.example ../.env

	# сгенерировать рандомные пароли для PostgreSQL
	`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 42 | xargs -i sed -i -e 's/POSTGRES_PASSWORD=[a-zA-Z0-9]*/POSTGRES_PASSWORD={}/' -e 's/DB_PASSWORD=[a-zA-Z0-9]*/DB_PASSWORD={}/' ../app/.env ../db/.env ../etl/.env`

	# сгенерировать рандомный пароль для суперпользователя в Django
	`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 10 | xargs -i sed -i 's/DJANGO_SUPERUSER_PASSWORD=[a-zA-Z0-9]*/DJANGO_SUPERUSER_PASSWORD={}/' ../app/.env`
	# сгенерировать рандомный SECRET_KEY
	`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | xargs -i sed -i 's/SECRET_KEY=[a-zA-Z0-9\-]*/SECRET_KEY={}/' ../app/.env`

	# установить HOST_UID = UID текущего пользователя. Это влияет на UID пользователя внутри контейнера.
	# Нужно для совместимости прав доступа к сгенерированным файлам у хостового пользователя
	`id -u | xargs -i sed -i 's/HOST_UID=.*/HOST_UID={}/' ../.env`
	`id -g | xargs -i sed -i 's/HOST_GID=.*/HOST_GID={}/' ../.env`

	`sed -i 's/PYTHONDONTWRITEBYTECODE=.*/PYTHONDONTWRITEBYTECODE=1/' ../api/.env`
.PHONY: env_setup

docker/build:	## build the environment
	$(DOCKER_COMPOSE) --env-file ../.env build
.PHONY: docker/build

docker/start:	## поднять Докер
	$(DOCKER_COMPOSE) --env-file ../.env up -d
.PHONY: docker/start

# alias for docker/start
docker/up: docker/start
.PHONY: docker/up

docker/stop:	## остановить все контейнеры Приложения
	$(DOCKER_COMPOSE) down
.PHONY: docker/stop

docker/down: 	## остановить и удалить все контейнеры Приложения
	$(DOCKER_COMPOSE) down --remove-orphans
.PHONY: docker/down

docker/destroy:	## остановить/удалить контейнеры и очистить данные Приложения
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
.PHONY: docker/destroy

#
# Приложение
#

app/init:	## инициализация Приложения
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py migrate --noinput
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py createsuperuser --noinput
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py compilemessages
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py collectstatic --no-input --clear
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py loaddata test_data.json
.PHONY: app/init

app/bash:		## доступ в контейнер с Django
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) bash
.PHONY: app/bash

app/log:	## посмотреть логи контейнера Приложения
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_APP)
.PHONY: app/log

app/test:	## test
	@echo $(STAGE)
.PHONY: app/test

app/fake_data:	## загрузить фейковых данных для тестирования
	$(DOCKER_COMPOSE) exec $(DOCKER_APP) python manage.py fake_data --count_genres 100 --count_persons 3000 --count_movies 20000
.PHONY: app/fake_data

#
# База данных
#

db/bash:		## доступ в контейнер с БД
	$(DOCKER_COMPOSE) exec $(DOCKER_DB) bash
.PHONY: db/bash

db/log:		## посмотреть логи контейнера БД
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_DB)
.PHONY: db/log

db/psql:		## интерактивный терминал PostgreSQL
	$(DOCKER_COMPOSE) exec $(DOCKER_DB) bash -c 'psql -U $${POSTGRES_USER} $${POSTGRES_DB}'
.PHONY: db/psql

db/waiting_for_readiness:
	$(DOCKER_COMPOSE) exec $(DOCKER_DB) bash -c 'until pg_isready 2>/dev/null; do sleep 1 ; done; echo "Database ready."'

#
# Nginx
#

nginx/bash:		## доступ в контейнер c Nginx
	$(DOCKER_COMPOSE) exec $(DOCKER_NGINX) bash
.PHONY: nginx/bash

nginx/log:		## посмотреть логи контейнера Nginx
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_NGINX)
.PHONY: nginx/log

#
# ETL - Сервис по перекачиванию данных из PostgreSQL в ElasticSearch
#

etl/init:	## инициализирует ElasticSearch
	$(DOCKER_COMPOSE) exec $(DOCKER_ETL) bash -c 'python3 init_es.py'
.PHONY: etl/init

etl/bash:	## доступ в контейнер с ETL
	$(DOCKER_COMPOSE) exec $(DOCKER_ETL) bash
.PHONY: etl/bash

etl/log: 	## посмотреть логи контейнера etl
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_ETL)
.PHONY: etl/log

etl/test: 	## авто-тесты
	$(DOCKER_COMPOSE) exec $(DOCKER_ETL) bash -c 'PYTHONPATH=. pytest -rP tests'
.PHONY: etl/test

etl/pipe:	## запустить pipe перекачки данных из Pg в ES
	$(DOCKER_COMPOSE) exec $(DOCKER_ETL) python etl.py
.PHONY: etl/pipe

#
# ElasticSearch
#

es/bash:	## доступ в контейнер с ElasticSearch
	$(DOCKER_COMPOSE) exec $(DOCKER_ES) bash
.PHONY: es/bash

es/waiting_for_readiness:
	$(DOCKER_COMPOSE) exec $(DOCKER_ES) bash -c 'until curl --silent --output /dev/null http://localhost:9200/_cat/health?h=st; do printf "."; sleep 3; done; echo "ES ready."'

#
# API
#

api/bash:	## доступ к контейнеру с FastAPI
	$(DOCKER_COMPOSE) exec $(DOCKER_API) bash
.PHONY: api/bash

api/log:	## посмотреть логи контейнера на хостовой машине
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_API)
.PHONY: api/logs

#
# Функкциональное тестирование
#

env_test_setup:		## настроить переменные окружения для тестового контура
	@cp ../api/.env.test.example ../api/.env
.PHONY: env_setup

test/destroy:		## остановить/удалить контейнеры для тестов и очистить тестовые данные
	$(DOCKER_COMPOSE_TEST) down --volumes --remove-orphans
.PHONY: test/setup

test/build: 	## собрать тестовые контейнеры
	$(DOCKER_COMPOSE_TEST) build
.PHONY: test/build

test/up: 	## поднять контейнеры для тестов
	$(DOCKER_COMPOSE_TEST) up -d
.PHONY: test/up

test/es_waiting_for_readiness:	## ожидать готовности ElasticSearchh
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_ES_TEST) bash -c 'until curl --silent --output /dev/null http://localhost:9200/_cat/health?h=st; do printf "."; sleep 3; done; echo "ES ready."'
.PHONY: test/es_waiting_for_readiness

test/redis_waiting_for_readiness:	## ожидать готовности Redis
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_REDIS_TEST) sh -c 'until redis-cli -u redis://localhost:6379 ping 1>/dev/null; do printf "."; sleep 1; done; echo "Redis ready."'
.PHONY: test/redis_waiting_for_readiness

test/run:	## запустить функциональные тесты API
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_API_TEST) bash -c 'cd /usr/src/app_tests/functional/ && PYTHONPATH=. pytest .'
.PHONY: test/run