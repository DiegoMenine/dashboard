#!/bin/bash

# Script de Deploy para Dashboard VoIP (Aceita Root)
# Execute este script no diretório do projeto

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Banner
echo -e "${BLUE}"
echo "=================================================="
echo "    🎯 DASHBOARD VOIP - DEPLOY ROOT"
echo "=================================================="
echo -e "${NC}"

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    error "Execute este script no diretório do projeto (onde está o docker-compose.yml)"
fi

log "Iniciando deploy do Dashboard VoIP..."

# Atualizar sistema
log "Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
log "Instalando dependências..."
apt install -y \
    curl \
    wget \
    git \
    ufw \
    fail2ban \
    htop \
    vim \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Instalar Docker
log "Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    log "Docker instalado com sucesso"
else
    log "Docker já está instalado"
fi

# Instalar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log "Instalando Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log "Docker Compose instalado com sucesso"
else
    log "Docker Compose já está instalado"
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    log "Criando arquivo de configuração .env..."
    cat > .env << EOF
# Configurações do MySQL
MYSQL_ROOT_PASSWORD=voip123456
MYSQL_DATABASE=sippulse_reports
MYSQL_USER=voip_user
MYSQL_PASSWORD=voip123456

# Configurações do Dashboard
FLASK_DEBUG=False
ENVIRONMENT=production

# Configurações SSH (edite conforme necessário)
SSH_HOST=200.159.177.191
SSH_USER=root
SSH_PASS=Tel1YccR^oOZjJ4
EOF
else
    log "Arquivo .env já existe"
fi

# Criar diretórios necessários
log "Criando diretórios..."
mkdir -p logs imports backups ssl mysql_config

# Gerar certificados SSL auto-assinados (para desenvolvimento)
log "Gerando certificados SSL..."
if [ ! -f ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -subj "/C=BR/ST=SP/L=Sao Paulo/O=VoIP Dashboard/CN=localhost"
    log "Certificados SSL gerados"
fi

# Configurar firewall
log "Configurando firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
log "Firewall configurado"

# Configurar fail2ban
log "Configurando fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban
log "Fail2ban configurado"

# Construir e iniciar containers
log "Construindo containers..."
docker-compose -f docker-compose.yml build

log "Iniciando serviços..."
docker-compose -f docker-compose.yml up -d

# Aguardar serviços ficarem prontos
log "Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos containers
log "Verificando status dos containers..."
docker-compose -f docker-compose.yml ps

# Testar conectividade
log "Testando conectividade..."
if curl -f http://localhost:5000/api/overview > /dev/null 2>&1; then
    log "Dashboard está funcionando!"
else
    warn "Dashboard pode não estar totalmente pronto ainda"
fi

# Configurar cron job para importação
log "Configurando cron job..."
CRON_JOB="0 2 * * * cd $(pwd) && docker-compose exec -T dashboard python importador.py >> logs/import.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
log "Cron job configurado"

# Criar script de manutenção
log "Criando script de manutenção..."
cat > manage.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        docker-compose up -d
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        ;;
    logs)
        docker-compose logs -f
        ;;
    update)
        git pull
        docker-compose build
        docker-compose up -d
        ;;
    backup)
        docker-compose exec mysql mysqldump -u root -pvoip123456 sippulse_reports > backups/backup_$(date +%Y%m%d_%H%M%S).sql
        ;;
    status)
        docker-compose ps
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|logs|update|backup|status}"
        exit 1
        ;;
esac
EOF

chmod +x manage.sh

# Configurar logrotate
log "Configurando logrotate..."
tee /etc/logrotate.d/voip-dashboard > /dev/null << EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f $(pwd)/docker-compose.yml restart dashboard
    endscript
}
EOF

# Finalização
echo -e "${BLUE}"
echo "=================================================="
echo "    ✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=================================================="
echo -e "${NC}"

log "Dashboard VoIP está disponível em:"
echo -e "${GREEN}  🌐 http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo -e "${GREEN}  🔒 https://$(hostname -I | awk '{print $1}'):443${NC}"

log "Comandos úteis:"
echo -e "${YELLOW}  📊 Status: ./manage.sh status${NC}"
echo -e "${YELLOW}  📝 Logs: ./manage.sh logs${NC}"
echo -e "${YELLOW}  🔄 Restart: ./manage.sh restart${NC}"
echo -e "${YELLOW}  💾 Backup: ./manage.sh backup${NC}"

log "Próximos passos:"
echo -e "${BLUE}  1. Configure as credenciais SSH no arquivo .env${NC}"
echo -e "${BLUE}  2. Teste a importação: docker-compose exec dashboard python importador.py${NC}"
echo -e "${BLUE}  3. Configure um domínio e certificados SSL reais${NC}"
echo -e "${BLUE}  4. Configure monitoramento e alertas${NC}"

log "Deploy concluído! 🎉" 