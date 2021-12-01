ifndef VERBOSE
.SILENT:
endif

.DEFAULT_GOAL := help

help:	## список доступных команд
	@grep -E '^[a-zA-Z0-9_\-\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "(Other less used targets are available, open Makefile for details)"
.PHONY: help

# вызываем make находящийся в подкаталоге с настройками окружения
SUBMAKE_DEVOPS=$(MAKE) --silent -C devops/docker

dev/setup:	## настроить инфраструктуру для разработки в Докере
	$(SUBMAKE_DEVOPS) env_setup
	$(SUBMAKE_DEVOPS) docker/destroy
	$(SUBMAKE_DEVOPS) docker/build
	$(SUBMAKE_DEVOPS) docker/up
	$(SUBMAKE_DEVOPS) db/waiting_for_readiness
	$(SUBMAKE_DEVOPS) app/init
	$(SUBMAKE_DEVOPS) es/waiting_for_readiness
	$(SUBMAKE_DEVOPS) etl/init
.PHONY: dev/setup


dev/up:	## поднять всю инфраструктуру для разработки в Докере
	$(SUBMAKE_DEVOPS) docker/up	
.PHONY: dev/up


dev/code:	## перейти внуть Докер-контейнера с API и начать кодить
	$(SUBMAKE_DEVOPS) docker/up
	$(SUBMAKE_DEVOPS) api/bash
.PHONY: dev/code

dev/log:	## подсмотреть логи контейнера на хостовой машине
	$(SUBMAKE_DEVOPS) api/log
.PHONY: dev/log

dev/stop:	## опустить инфраструктуру разработки
	$(SUBMAKE_DEVOPS) docker/stop
.PHONY: dev/stop