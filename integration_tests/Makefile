.PHONY: test-setup test egg-info pull-images agentd db

MANAGE_DB_DIR ?= ../../xivo-manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/postgres-test/Dockerfile

test-setup: egg-info pull-images agentd

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

pull-images:
	docker pull rabbitmq
	docker pull wazopbx/postgres-test
	docker pull wazopbx/wait
	docker pull wazopbx/wazo-auth-mock

agentd:
	docker build -t wazopbx/wazo-agentd ..
	$(MAKE) agentd-test

agentd-test: egg-info
	docker build --no-cache -t wazo-agentd-test -f Dockerfile-agentd ..

db:
	docker build --no-cache -t wazopbx/postgres-test -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)
