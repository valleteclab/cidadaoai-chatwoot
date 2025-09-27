#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Instalando Certbot e gerando certificado SSL...${NC}"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Por favor, execute como root (sudo)${NC}"
    exit 1
fi

# Instalar Certbot e plugin Nginx
echo -e "${YELLOW}Instalando Certbot...${NC}"
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Verificar se o domínio está configurado
DOMAIN="chat.sisgov.app.br"
echo -e "${YELLOW}Verificando DNS para $DOMAIN...${NC}"
if ! host $DOMAIN > /dev/null; then
    echo -e "${RED}Erro: Não foi possível resolver o domínio $DOMAIN${NC}"
    echo -e "${YELLOW}Verifique se o DNS está configurado corretamente${NC}"
    exit 1
fi

# Parar Nginx temporariamente
echo -e "${YELLOW}Parando Nginx...${NC}"
systemctl stop nginx

# Gerar certificado
echo -e "${YELLOW}Gerando certificado para $DOMAIN...${NC}"
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email contato@sisgov.app.br \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Certificado gerado com sucesso!${NC}"
    
    # Verificar certificado
    echo -e "${YELLOW}Verificando certificado...${NC}"
    certbot certificates
    
    # Iniciar Nginx
    echo -e "${YELLOW}Iniciando Nginx...${NC}"
    systemctl start nginx
    
    echo -e "${GREEN}Configuração SSL concluída!${NC}"
    echo -e "${YELLOW}Agora você pode executar install-nginx.sh para configurar o proxy reverso${NC}"
else
    echo -e "${RED}Erro ao gerar certificado${NC}"
    echo -e "${YELLOW}Iniciando Nginx...${NC}"
    systemctl start nginx
    exit 1
fi

# Configurar renovação automática
echo -e "${YELLOW}Configurando renovação automática...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

echo -e "${GREEN}Tudo pronto! O certificado será renovado automaticamente${NC}"
