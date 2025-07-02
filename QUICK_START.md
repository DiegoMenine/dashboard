# 🚀 Quick Start - Dashboard VoIP

## Deploy Rápido no VPS Debian 11

### 1. Preparar o VPS

```bash
# Conectar ao VPS
ssh root@seu-vps-ip

# Criar usuário (recomendado)
adduser voipuser
usermod -aG sudo voipuser
su - voipuser
```

### 2. Deploy Automatizado

```bash
# Baixar e executar deploy
wget https://raw.githubusercontent.com/seu-usuario/voip-dashboard/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 3. Acessar o Dashboard

- **HTTP**: http://IP-DO-VPS:5000
- **HTTPS**: https://IP-DO-VPS:443

### 4. Configurar Credenciais SSH

Edite o arquivo `.env`:

```bash
SSH_HOST=200.159.177.191
SSH_USER=root
SSH_PASS=Tel1YccR^oOZjJ4
```

### 5. Testar Importação

```bash
# Teste manual
docker-compose exec dashboard python importador.py

# Verificar logs
tail -f logs/import.log
```

## 📊 Comandos Úteis

```bash
# Status dos serviços
./manage.sh status

# Ver logs
./manage.sh logs

# Backup do banco
./manage.sh backup

# Reiniciar serviços
./manage.sh restart
```

## 🎯 Próximos Passos

1. Configure domínio real
2. Instale certificados SSL (Let's Encrypt)
3. Configure monitoramento
4. Configure backup externo

---

**🎉 Sistema pronto em 5 minutos!**
