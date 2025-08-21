#!/usr/bin/env bash
set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y curl ca-certificates gnupg lsb-release
fi

# Docker Engine + compose plugin
if ! command -v docker >/dev/null 2>&1; then
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER" || true
fi

sudo mkdir -p /backups/pg /backups/media

# UFW allow 8000 if ufw exists
if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow 8000/tcp || true
fi

echo "Listo. Reinicia la sesión para aplicar pertenencia a grupo docker."
echo "Siguientes pasos:"
echo "1) cd /home/paolo/pm-flask && cp .env.example .env && edita SECRET_KEY"
echo "2) bash scripts/first_run.sh"
