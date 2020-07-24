MANAGE_DB_DIR ?= ../../xivo-manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile

test-setup: egg-info agentd agentd-test

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

agentd:
	docker build -t wazopbx/wazo-agentd ..

agentd-test: egg-info
	docker build --no-cache -t wazo-agentd-test -f Dockerfile-agentd ..

db:
	docker build --no-cache -t wazopbx/wazo-confd-db-test -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

.PHONY: test-setup test egg-info agentd agentd-test db
