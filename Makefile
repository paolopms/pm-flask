.PHONY: dev compose-up compose-down migrate seed test backup-db backup-media restore-db fmt lint typecheck smoke

VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
FLASK?=$(VENV)/bin/flask

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

.dev-env: $(VENV)/bin/activate
	@echo "OK" > .dev-env

run: .dev-env
	FLASK_APP=petmaison.app:app FLASK_ENV=development $(FLASK) run -p 8000 -h 0.0.0.0

dev: .dev-env
	FLASK_APP=petmaison.app:app FLASK_ENV=development $(FLASK) run -p 8000 -h 0.0.0.0

compose-up:
	docker compose up -d

compose-down:
	docker compose down --remove-orphans

migrate: .dev-env
	FLASK_APP=petmaison.app:app $(FLASK) db migrate -m "auto"
	FLASK_APP=petmaison.app:app $(FLASK) db upgrade

seed: .dev-env
	FLASK_APP=petmaison.app:app $(FLASK) seed

test: .dev-env
	pytest -q

fmt:
	$(VENV)/bin/isort petmaison tests
	$(VENV)/bin/black petmaison tests

lint:
	$(VENV)/bin/flake8 petmaison

typecheck:
	$(VENV)/bin/mypy petmaison

backup-db:
	bash scripts/backup_db.sh

backup-media:
	bash scripts/backup_media.sh

restore-db:
	bash scripts/restore_db.sh $(FILE)

smoke:
	bash scripts/smoke_test.sh
