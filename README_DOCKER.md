# 🐳 Dashboard VoIP - Deploy com Docker

Solução completa de deploy automatizado para VPS Debian 11 usando Docker e Docker Compose.

## 🚀 Deploy Rápido

### 1. Preparar o VPS

```bash
# Conectar ao seu VPS
ssh root@seu-vps-ip

# Criar usuário não-root (recomendado)
adduser voipuser
usermod -aG sudo voipuser
su - voipuser
```

### 2. Executar Deploy Automatizado

```bash
# Baixar o script de deploy
wget https://raw.githubusercontent.com/seu-usuario/voip-dashboard/main/deploy.sh
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

O script irá:

- ✅ Instalar Docker e Docker Compose
- ✅ Configurar firewall e fail2ban
- ✅ Criar estrutura de diretórios
- ✅ Gerar certificados SSL
- ✅ Construir e iniciar containers
- ✅ Configurar cron job
- ✅ Criar scripts de manutenção

## 📁 Estrutura do Projeto

```
/opt/voip-dashboard/
├── docker-compose.yml          # Configuração dos containers
├── docker-compose.prod.yml     # Versão de produção com Nginx
├── Dockerfile                  # Imagem do dashboard
├── nginx.conf                  # Configuração do Nginx
├── deploy.sh                   # Script de deploy
├── manage.sh                   # Script de manutenção
├── .env                        # Variáveis de ambiente
├── logs/                       # Logs da aplicação
├── imports/                    # Arquivos importados
├── backups/                    # Backups do banco
├── ssl/                        # Certificados SSL
└── mysql_config/              # Configurações do MySQL
```

## 🐳 Containers

### Dashboard (Flask)

- **Porta**: 5000
- **Imagem**: Customizada com Python 3.11
- **Volumes**: logs, imports, backups
- **Health Check**: `/api/overview`

### MySQL 8.0

- **Porta**: 3306
- **Database**: sippulse_reports
- **Volumes**: mysql_data (persistente)
- **Health Check**: mysqladmin ping

### Nginx (Produção)

- **Portas**: 80, 443
- **Proxy reverso** para o dashboard
- **SSL/TLS** com certificados
- **Rate limiting** e segurança

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# MySQL
MYSQL_ROOT_PASSWORD=voip123456
MYSQL_DATABASE=sippulse_reports
MYSQL_USER=voip_user
MYSQL_PASSWORD=voip123456

# Dashboard
FLASK_DEBUG=False
ENVIRONMENT=production

# SSH (edite conforme necessário)
SSH_HOST=200.159.177.191
SSH_USER=root
SSH_PASS=Tel1YccR^oOZjJ4
```

### Comandos de Gerenciamento

```bash
# Status dos containers
./manage.sh status

# Iniciar serviços
./manage.sh start

# Parar serviços
./manage.sh stop

# Reiniciar serviços
./manage.sh restart

# Ver logs
./manage.sh logs

# Atualizar aplicação
./manage.sh update

# Backup do banco
./manage.sh backup
```

## 🔧 Manutenção

### Logs

```bash
# Logs do dashboard
docker-compose logs dashboard

# Logs do MySQL
docker-compose logs mysql

# Logs do Nginx
docker-compose logs nginx

# Todos os logs
docker-compose logs -f
```

### Backup e Restore

```bash
# Backup automático
./manage.sh backup

# Backup manual
docker-compose exec mysql mysqldump -u root -pvoip123456 sippulse_reports > backup.sql

# Restore
docker-compose exec -T mysql mysql -u root -pvoip123456 sippulse_reports < backup.sql
```

### Monitoramento

```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Health checks
docker-compose exec dashboard curl -f http://localhost:5000/api/overview
```

## 🔒 Segurança

### Firewall (UFW)

- SSH (22)
- HTTP (80)
- HTTPS (443)
- Dashboard (5000)

### Fail2ban

- Proteção contra ataques SSH
- Logs em `/var/log/fail2ban.log`

### SSL/TLS

- Certificados auto-assinados (desenvolvimento)
- Configure certificados reais para produção

## 📊 Monitoramento

### Health Checks

- Dashboard: `/api/overview`
- MySQL: `mysqladmin ping`
- Nginx: `/health`

### Logs Automáticos

- Logrotate configurado
- Rotação diária
- Compressão automática
- Retenção de 30 dias

## 🚨 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker-compose logs dashboard

# Verificar configuração
docker-compose config

# Reconstruir imagem
docker-compose build --no-cache
```

### Problemas de conectividade

```bash
# Testar conectividade interna
docker-compose exec dashboard ping mysql

# Verificar variáveis de ambiente
docker-compose exec dashboard env | grep DB_

# Testar conexão com banco
docker-compose exec dashboard python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='mysql',
    user='voip_user',
    password='voip123456',
    database='sippulse_reports'
)
print('Conexão OK')
conn.close()
"
```

### Problemas de importação

```bash
# Testar importação manual
docker-compose exec dashboard python importador.py

# Verificar logs de importação
tail -f logs/import.log

# Verificar conectividade SSH
docker-compose exec dashboard ssh -o ConnectTimeout=10 root@200.159.177.191
```

## 🔄 Atualizações

### Atualizar Aplicação

```bash
# Pull das mudanças
git pull

# Reconstruir e reiniciar
./manage.sh update
```

### Atualizar Docker

```bash
# Atualizar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 📈 Escalabilidade

### Para Produção

1. Configure domínio real
2. Instale certificados SSL reais (Let's Encrypt)
3. Configure monitoramento (Prometheus/Grafana)
4. Configure backup externo
5. Configure alertas por email

### Para Alta Disponibilidade

1. Use Docker Swarm ou Kubernetes
2. Configure load balancer
3. Use banco de dados externo (RDS)
4. Configure backup em nuvem
5. Configure monitoramento avançado

## 🆘 Suporte

### Comandos Úteis

```bash
# Informações do sistema
docker system df
docker system prune

# Limpar recursos não utilizados
docker system prune -a

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos
htop
```

### Logs Importantes

- Dashboard: `logs/app.log`
- Importação: `logs/import.log`
- Nginx: `docker-compose logs nginx`
- MySQL: `docker-compose logs mysql`
- Sistema: `/var/log/syslog`

## 🎯 Próximos Passos

1. **Configure credenciais SSH** no arquivo `.env`
2. **Teste a importação** manualmente
3. **Configure domínio** e certificados SSL reais
4. **Configure monitoramento** e alertas
5. **Configure backup** externo
6. **Documente procedimentos** específicos da sua empresa

---

**🎉 Sistema pronto para uso em produção!**
