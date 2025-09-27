#!/bin/bash

# Script de instalação do CidadaoAI Chatwoot no servidor
# Execute este script no servidor

set -e  # Parar se houver erro

echo "🚀 Iniciando instalação do CidadaoAI Chatwoot..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    print_error "Arquivo docker-compose.yml não encontrado!"
    print_error "Execute este script no diretório do projeto cidadaoai-chatwoot"
    exit 1
fi

print_success "Diretório correto encontrado"

# 2. Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_warning "Docker não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    print_success "Docker instalado. Você pode precisar fazer logout/login para usar Docker sem sudo"
else
    print_success "Docker já está instalado"
fi

# 3. Verificar portas em uso
print_status "Verificando portas em uso..."
if netstat -tulpn 2>/dev/null | grep -q ":5433\|:6380\|:8081"; then
    print_warning "Algumas portas (5433, 6380, 8081) estão em uso"
    print_warning "Verificando quais processos estão usando..."
    netstat -tulpn | grep -E ":(5433|6380|8081)"
fi

# 4. Parar containers existentes (se houver)
print_status "Parando containers existentes..."
docker compose down 2>/dev/null || true

# 5. Iniciar containers
print_status "Iniciando containers Docker..."
docker compose up -d

# 6. Aguardar containers iniciarem
print_status "Aguardando containers iniciarem..."
sleep 10

# 7. Verificar status dos containers
print_status "Verificando status dos containers..."
docker compose ps

# 8. Verificar logs
print_status "Verificando logs do PostgreSQL..."
docker compose logs postgres | tail -10

print_status "Verificando logs do Redis..."
docker compose logs redis | tail -10

# 9. Testar conexões
print_status "Testando conexão com PostgreSQL..."
if docker exec cidadaoai_postgres pg_isready -U cidadaoai_user -d cidadaoai; then
    print_success "PostgreSQL está funcionando!"
else
    print_error "Problema com PostgreSQL"
fi

print_status "Testando conexão com Redis..."
if docker exec cidadaoai_redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis está funcionando!"
else
    print_error "Problema com Redis"
fi

# 10. Verificar se o schema foi carregado
print_status "Verificando se o schema foi carregado..."
TABLES=$(docker exec cidadaoai_postgres psql -U cidadaoai_user -d cidadaoai -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
if [ "$TABLES" -gt 0 ]; then
    print_success "Schema carregado com sucesso! ($TABLES tabelas encontradas)"
else
    print_warning "Schema pode não ter sido carregado. Verifique o arquivo docs/schema.sql"
fi

# 11. Mostrar informações de acesso
echo ""
print_success "🎉 Instalação concluída!"
echo ""
echo "📋 Informações de acesso:"
echo "  PostgreSQL: localhost:5433"
echo "    Usuário: cidadaoai_user"
echo "    Senha: cidadaoai_senha_2024"
echo "    Banco: cidadaoai"
echo ""
echo "  Redis: localhost:6380"
echo ""
echo "  pgAdmin: http://localhost:8081"
echo "    Email: admin@cidadaoai.com"
echo "    Senha: admin123"
echo ""
echo "🔧 Próximos passos:"
echo "  1. Copie env-docker.template para .env"
echo "  2. Configure suas chaves de API no .env"
echo "  3. Ative o ambiente virtual: source venv/bin/activate"
echo "  4. Instale dependências: pip install -r requirements.txt"
echo "  5. Teste a aplicação: python backend/main.py"
echo ""
print_status "Para ver logs em tempo real: docker compose logs -f"
print_status "Para parar os containers: docker compose down"
print_status "Para reiniciar: docker compose restart"
