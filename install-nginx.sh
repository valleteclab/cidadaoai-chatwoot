#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Instalando configuração do Nginx para Cidadão.AI...${NC}"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Por favor, execute como root (sudo)${NC}"
    exit 1
fi

# Verificar se o Nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}Nginx não está instalado${NC}"
    exit 1
fi

# Verificar se os certificados existem
if [ ! -f "/etc/letsencrypt/live/chat.sisgov.app.br/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/chat.sisgov.app.br/privkey.pem" ]; then
    echo -e "${RED}Certificados SSL não encontrados em /etc/letsencrypt/live/chat.sisgov.app.br/${NC}"
    exit 1
fi

# Backup da configuração atual
echo -e "${YELLOW}Fazendo backup da configuração atual...${NC}"
BACKUP_DIR="/etc/nginx/sites-available/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /etc/nginx/sites-available/* "$BACKUP_DIR/"
echo -e "${GREEN}Backup salvo em $BACKUP_DIR${NC}"

# Copiar nova configuração
echo -e "${YELLOW}Instalando nova configuração...${NC}"
cp nginx/cidadaoai.conf /etc/nginx/sites-available/cidadaoai.conf

# Criar link simbólico se não existir
if [ ! -f "/etc/nginx/sites-enabled/cidadaoai.conf" ]; then
    ln -s /etc/nginx/sites-available/cidadaoai.conf /etc/nginx/sites-enabled/
fi

# Testar configuração
echo -e "${YELLOW}Testando configuração do Nginx...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}Reiniciando Nginx...${NC}"
    systemctl restart nginx
    echo -e "${GREEN}Configuração instalada com sucesso!${NC}"
    echo -e "${GREEN}Agora você pode acessar: https://chat.sisgov.app.br/tecnico${NC}"
else
    echo -e "${RED}Erro na configuração do Nginx${NC}"
    echo -e "${YELLOW}Restaurando backup...${NC}"
    cp "$BACKUP_DIR"/* /etc/nginx/sites-available/
    systemctl restart nginx
    exit 1
fi
