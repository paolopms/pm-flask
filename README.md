# PetMaison (Flask) - Infra y Despliegue

Aplicación de gestión para PetMaison (Chile) con Flask + PostgreSQL. Incluye CI/CD, scripts de operación, systemd y Docker Compose.

## A) Resumen App
- Blueprints: auth, dashboard, customers, products, suppliers, purchases, sales (POS), orders, inventory, reports, api.
- DB: PostgreSQL 16 (prod), SQLite (dev). Migraciones con Alembic.
- Auth: Flask-Login, roles `admin` y `vendedor`.
- UI: Jinja2 + Bootstrap 5 + htmx. Chart.js para dashboard.
- Reportes: CSV y boleta PDF (pendiente integrar plantillas PDF finales).
- Seeds: usuarios y datos demo.
- Tests: IVA 19%, ticket promedio, costo promedio ponderado, stock en confirmaciones (pendiente completar suite).

## B) Contenedores y arranque
- Dockerfile multi-stage (gunicorn en 8000)
- docker-compose.yml con servicios `db` (postgres:16) y `web` (app), volumen `media_data` y healthcheck.

`.env.example`:
```
FLASK_ENV=production
SECRET_KEY=change_me
TIME_ZONE=America/Santiago
DATABASE_URL=postgresql+psycopg://petmaison:superseguro@db:5432/petmaison
SQLITE_URL=sqlite:///instance/dev.db
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/static
```

Makefile:
- `make dev`, `make compose-up`, `make compose-down`, `make migrate`, `make seed`, `make test`, `make backup-db`, `make backup-media`, `make restore-db FILE=...`, `make smoke`.

## C) Scripts de operación (`scripts/`)
- `bootstrap_ubuntu.sh`: instala Docker + compose plugin, crea `/backups/{pg,media}`, abre 8000 en UFW si existe, y muestra siguientes pasos.
- `first_run.sh`: `docker compose up -d db` → `flask db upgrade` → `flask seed` → `docker compose up -d web`.
- Backups: `backup_db.sh`, `restore_db.sh`, `backup_media.sh`.
- `smoke_test.sh`: verifica `/health` y `/api/docs`.
- `rollback.sh`: baja web, levanta imagen previa (requiere tag) y ejecuta smoke test.

Todos con `set -euo pipefail`. Recuerda otorgar permisos: `chmod +x scripts/*.sh` (ya aplicado).

## D) Systemd (arranque automático)
Archivo: `systemd/pm-flask.service`

Instalar:
```bash
sudo cp systemd/pm-flask.service /etc/systemd/system/pm-flask.service
sudo systemctl daemon-reload
sudo systemctl enable --now pm-flask
```

## E) CI/CD con GitHub Actions
Workflow: `.github/workflows/deploy.yml`
- Build & Test: instala deps y ejecuta `pytest`.
- Build imagen Docker y push a GHCR (`ghcr.io/<org>/<repo>:<SHA>` y `:latest`).
- Deploy por SSH al VPS: `docker compose up -d db` → `flask db upgrade` → `docker compose up -d web` → `scripts/smoke_test.sh` → si falla, `scripts/rollback.sh`.

Secrets necesarios:
- `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_PORT` (opcional)
- `APP_DIR` (ej: `/home/paolo/pm-flask`)
- GHCR usa el `GITHUB_TOKEN` por defecto para push/pull.

## F) Seguridad básica
- `.dockerignore` y `.gitignore` protegen `.env`, `media/`, `backups/`.
- CSRF habilitado. Sesiones seguras.
- Logging a stdout; `gunicorn.conf.py` incluido.

## G) Instalación

### Local (sin Docker, SQLite)
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=petmaison.app:app FLASK_ENV=development
flask db upgrade
flask seed
flask run -p 8000 -h 0.0.0.0
```

### Servidor (Docker + Postgres)
```bash
cd /home/paolo/pm-flask
cp .env.example .env
sudo bash scripts/bootstrap_ubuntu.sh
bash scripts/first_run.sh
```
Accede: `http://TU_IP:8000`

Backups (cron ejemplos):
```
0 3 * * * PGHOST=127.0.0.1 PGUSER=petmaison PGPASSWORD=superseguro PGDATABASE=petmaison BACKUP_DIR=/backups/pg /home/paolo/pm-flask/scripts/backup_db.sh && find /backups/pg -type f -mtime +14 -delete
10 3 * * * docker compose -f /home/paolo/pm-flask/docker-compose.yml run --rm web /app/scripts/backup_media.sh && find /backups/media -type f -mtime +14 -delete
```

## H) Extras
- `/health` devuelve 200 JSON.
- Filtros Jinja: `clp` y `es_date`.
- Índices en SKU, fechas y FKs; transacciones en confirmaciones.

## Troubleshooting
- Ver logs: `docker compose logs -f web`
- Permisos volumenes: asegurar que `media_data` exista y permita escritura.
- Migraciones: `docker compose run --rm web flask db downgrade/upgrade`.
