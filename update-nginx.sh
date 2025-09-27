#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Atualizando configuração do Nginx para Cidadão.AI...${NC}"

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

# Encontrar arquivo de configuração do Chatwoot
NGINX_CONF_DIR="/etc/nginx/sites-available"
CHATWOOT_CONF=$(find $NGINX_CONF_DIR -type f -exec grep -l "chat.sisgov.app.br" {} \;)

if [ -z "$CHATWOOT_CONF" ]; then
    echo -e "${RED}Configuração do Chatwoot não encontrada em $NGINX_CONF_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}Encontrada configuração do Chatwoot em: $CHATWOOT_CONF${NC}"

# Backup da configuração atual
echo -e "${YELLOW}Fazendo backup...${NC}"
BACKUP_FILE="${CHATWOOT_CONF}.bak_$(date +%Y%m%d_%H%M%S)"
cp "$CHATWOOT_CONF" "$BACKUP_FILE"
echo -e "${GREEN}Backup salvo em $BACKUP_FILE${NC}"

# Adicionar configurações do Cidadão.AI
echo -e "${YELLOW}Adicionando configurações do Cidadão.AI...${NC}"

# Procurar bloco server existente
if ! grep -q "location /tecnico {" "$CHATWOOT_CONF"; then
    # Adicionar antes do último }
    sed -i '$i\    # Cidadão.AI - Painel Técnico\n    location /tecnico {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n    }\n' "$CHATWOOT_CONF"
fi

if ! grep -q "location /api {" "$CHATWOOT_CONF"; then
    sed -i '$i\    # Cidadão.AI - API\n    location /api {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        client_max_body_size 20M;\n    }\n' "$CHATWOOT_CONF"
fi

if ! grep -q "location /socket.io {" "$CHATWOOT_CONF"; then
    sed -i '$i\    # Cidadão.AI - WebSocket\n    location /socket.io {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection "upgrade";\n        proxy_read_timeout 86400;\n    }\n' "$CHATWOOT_CONF"
fi

if ! grep -q "location /media {" "$CHATWOOT_CONF"; then
    sed -i '$i\    # Cidadão.AI - Media files\n    location /media {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        expires 1h;\n        add_header Cache-Control "public, no-transform";\n    }\n' "$CHATWOOT_CONF"
fi

if ! grep -q "location /static {" "$CHATWOOT_CONF"; then
    sed -i '$i\    # Cidadão.AI - Static files\n    location /static {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        expires 1h;\n        add_header Cache-Control "public, no-transform";\n    }\n' "$CHATWOOT_CONF"
fi

# Testar configuração
echo -e "${YELLOW}Testando configuração do Nginx...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}Reiniciando Nginx...${NC}"
    systemctl restart nginx
    echo -e "${GREEN}Configuração atualizada com sucesso!${NC}"
    echo -e "${GREEN}Agora você pode acessar: https://chat.sisgov.app.br/tecnico${NC}"
else
    echo -e "${RED}Erro na configuração do Nginx${NC}"
    echo -e "${YELLOW}Restaurando backup...${NC}"
    cp "$BACKUP_FILE" "$CHATWOOT_CONF"
    systemctl restart nginx
    exit 1
fi
