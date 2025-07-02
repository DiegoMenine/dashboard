# 🎯 Dashboard VoIP - Análise de Consumo

Sistema completo de análise e monitoramento de dados VoIP com dashboard web moderno, importação automática e insights inteligentes.

## 🚀 Funcionalidades Principais

### 📊 Dashboard Web

- **Interface moderna e responsiva** com Bootstrap 5
- **Cards de resumo** com métricas em tempo real
- **Gráficos interativos** usando Chart.js
- **Tabela detalhada** com filtros avançados
- **Insights automáticos** com detecção de anomalias
- **Atualização automática** a cada 5 minutos

### 🔄 Importação Automática

- **Conexão SSH** com servidor remoto
- **Download automático** de backups incrementais
- **Extração e importação** para MySQL
- **Execução via cron job** diariamente às 2h
- **Logs detalhados** de todas as operações

### 🧠 Insights Inteligentes

- **Detecção de anomalias** no volume de chamadas
- **Alertas automáticos** para taxas de erro altas
- **Top 5 callers/callees** com mais tráfego
- **Análise por provider** e rateplan
- **Métricas de custo** e duração

## 📋 Requisitos

- Python 3.8+
- MySQL 5.7+
- Acesso SSH ao servidor remoto
- Navegador web moderno

## 🛠️ Instalação Rápida

### 1. Setup Automatizado (Recomendado)

```bash
# Clone ou baixe os arquivos
cd dashboard

# Execute o setup automatizado
python3 setup.py
```

O script `setup.py` irá:

- ✅ Verificar requisitos
- ✅ Instalar dependências
- ✅ Configurar banco de dados
- ✅ Criar diretórios necessários
- ✅ Configurar cron job
- ✅ Criar scripts de inicialização

### 2. Instalação Manual

#### Instalar dependências:

```bash
pip install -r requirements.txt
```

#### Configurar banco de dados:

```sql
-- Execute o script database_setup.sql no MySQL
mysql -u root -p < database_setup.sql
```

#### Configurar importação:

Edite `importador.py` com suas credenciais SSH e MySQL.

## 🚀 Como Usar

### Iniciar o Dashboard

```bash
# Opção 1: Script de inicialização
./start_dashboard.sh

# Opção 2: Direto
python3 app.py
```

### Acessar o Dashboard

Abra seu navegador e acesse: **http://localhost:5000**

### Testar Importação Manual

```bash
python3 importador.py
```

### Verificar Logs

```bash
tail -f /var/log/importador_voip.log
```

## 📊 Funcionalidades do Dashboard

### Cards de Resumo

- **Total de chamadas** (hoje vs ontem)
- **Taxa de sucesso** (% de chamadas bem-sucedidas)
- **Duração média** (segundos por chamada)
- **Custo total** (valor gasto hoje)

### Gráficos

- **Evolução de chamadas** (linha temporal)
- **Distribuição por provider** (gráfico de pizza)
- **Sucesso vs erro** (comparativo)

### Tabela Detalhada

- **Filtros por data**, caller, callee, status
- **Paginação** para grandes volumes
- **Ordenação** por qualquer coluna
- **Exportação** de dados

### Insights Automáticos

- **Alertas** para taxas de erro > 10%
- **Anomalias** no volume de chamadas
- **Top performers** (callers/callees)

## ⚙️ Configurações

### Variáveis Importantes

#### SSH (importador.py)

```python
SSH_HOST = "200.159.177.191"
SSH_USER = "root"
SSH_PASS = "Tel1YccR^oOZjJ4"
REMOTE_DIR = "/srv/backups/voip-reports/"
```

#### MySQL (app.py)

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha_mysql",
    "database": "sippulse_reports"
}
```

### Cron Job

```bash
# Executar diariamente às 2h da manhã
0 2 * * * /usr/bin/python3 /opt/voip_import/importador.py >> /var/log/importador_voip.log 2>&1
```

## 📁 Estrutura do Projeto

```
dashboard/
├── app.py                 # Backend Flask
├── importador.py          # Script de importação
├── setup.py              # Setup automatizado
├── requirements.txt      # Dependências Python
├── database_setup.sql    # Script SQL do banco
├── start_dashboard.sh    # Script de inicialização
├── templates/
│   └── dashboard.html    # Template principal
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       └── dashboard.js  # JavaScript do dashboard
└── README.md             # Documentação
```

## 🔧 Manutenção

### Atualizar Dados

Os dados são atualizados automaticamente via cron job. Para atualização manual:

```bash
python3 importador.py
```

### Verificar Status

```bash
# Logs de importação
tail -f /var/log/importador_voip.log

# Status do cron job
crontab -l

# Processos do dashboard
ps aux | grep app.py
```

### Backup do Banco

```bash
mysqldump -u root -p sippulse_reports > backup_voip_$(date +%Y%m%d).sql
```

## 🚨 Troubleshooting

### Erro de Conexão SSH

- Verifique credenciais no `importador.py`
- Teste conexão: `ssh root@200.159.177.191`
- Verifique firewall/network

### Erro de Banco de Dados

- Verifique credenciais no `app.py`
- Teste conexão: `mysql -u root -p sippulse_reports`
- Verifique se a tabela `acc_report` existe

### Dashboard Não Carrega

- Verifique se o Flask está rodando: `ps aux | grep app.py`
- Verifique logs: `python3 app.py` (modo debug)
- Verifique porta 5000: `netstat -tlnp | grep 5000`

## 🔒 Segurança

⚠️ **Recomendações importantes:**

- Altere senhas padrão (SSH e MySQL)
- Use usuário específico para MySQL (não root)
- Configure firewall para restringir acesso
- Use HTTPS em produção
- Configure autenticação no dashboard
- Faça backups regulares

## 📞 Suporte

Para suporte técnico:

1. Verifique os logs em `/var/log/importador_voip.log`
2. Consulte a documentação neste README
3. Verifique se todos os requisitos estão atendidos

## 🎯 Próximas Funcionalidades

- [ ] Autenticação de usuários
- [ ] Relatórios em PDF
- [ ] Alertas por email
- [ ] API REST completa
- [ ] Integração com sistemas externos
- [ ] Dashboard mobile
- [ ] Análise preditiva
- [ ] Backup automático
