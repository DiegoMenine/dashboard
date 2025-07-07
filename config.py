# Configurações do Dashboard VoIP
# Centralize todas as configurações aqui para facilitar manutenção

import os
from pathlib import Path

# === CONFIGURAÇÕES SSH ===
SSH_CONFIG = {
    "host": os.getenv("SSH_HOST", "200.159.177.191"),
    "user": os.getenv("SSH_USER", "root"),
    "password": os.getenv("SSH_PASS", "Tel1YccR^oOZjJ4"),
    "remote_dir": "/srv/backups/voip-reports/",
    "local_dir": "/opt/voip_import/"
}

# === CONFIGURAÇÕES DO BANCO DE DADOS ===
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),  # Nome do container MySQL no docker-compose
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "voip123456"),
    "database": os.getenv("DB_NAME", "sippulse_reports"),
    "charset": "utf8mb4",
    "autocommit": True
}

# === CONFIGURAÇÕES DO FLASK ===
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": os.getenv("FLASK_DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "voip-dashboard-secret-key-change-in-production")
}

# === CONFIGURAÇÕES DE LOG ===
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "/var/log/voip_dashboard/app.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# === CONFIGURAÇÕES DO DASHBOARD ===
DASHBOARD_CONFIG = {
    "title": "Dashboard VoIP - Análise de Consumo",
    "refresh_interval": 300000,  # 5 minutos em ms
    "items_per_page": 50,
    "max_chart_points": 30,  # Máximo de pontos nos gráficos
    "anomaly_threshold": 2.0,  # Desvio padrão para detectar anomalias
    "error_rate_threshold": 10.0  # Taxa de erro em % para alertas
}

# === CONFIGURAÇÕES DE CRON ===
CRON_CONFIG = {
    "schedule": "0 2 * * *",  # Diariamente às 2h da manhã
    "log_file": "/var/log/importador_voip.log",
    "python_path": "/usr/bin/python3"
}

# === CONFIGURAÇÕES DE SEGURANÇA ===
SECURITY_CONFIG = {
    "session_timeout": 3600,  # 1 hora
    "max_login_attempts": 5,
    "password_min_length": 8,
    "require_https": os.getenv("REQUIRE_HTTPS", "False").lower() == "true"
}

# === CONFIGURAÇÕES DE EMAIL (FUTURO) ===
EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "from_email": "voip-dashboard@example.com",
    "to_emails": []
}

# === CONFIGURAÇÕES DE BACKUP ===
BACKUP_CONFIG = {
    "enabled": True,
    "schedule": "0 1 * * *",  # Diariamente às 1h da manhã
    "retention_days": 30,
    "backup_dir": "/opt/voip_backups/",
    "compress": True
}

# === FUNÇÕES DE CONFIGURAÇÃO ===

def get_db_connection_string():
    """Retorna string de conexão do banco de dados"""
    return f"mysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

def get_cron_command():
    """Retorna comando completo do cron job"""
    return f"{CRON_CONFIG['schedule']} {CRON_CONFIG['python_path']} {SSH_CONFIG['local_dir']}importador.py >> {CRON_CONFIG['log_file']} 2>&1"

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        SSH_CONFIG['local_dir'],
        Path(LOG_CONFIG['file']).parent,
        BACKUP_CONFIG['backup_dir']
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def validate_config():
    """Valida as configurações"""
    errors = []
    
    # Validar configurações SSH
    if not SSH_CONFIG['host'] or not SSH_CONFIG['user'] or not SSH_CONFIG['password']:
        errors.append("Configurações SSH incompletas")
    
    # Validar configurações do banco
    if not DB_CONFIG['host'] or not DB_CONFIG['user'] or not DB_CONFIG['password']:
        errors.append("Configurações do banco de dados incompletas")
    
    # Validar diretórios
    if not SSH_CONFIG['local_dir']:
        errors.append("Diretório local não configurado")
    
    return errors

# === CONFIGURAÇÕES DE AMBIENTE ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Configurações específicas para produção
    FLASK_CONFIG["debug"] = False
    SECURITY_CONFIG["require_https"] = True
    LOG_CONFIG["level"] = "WARNING"
elif ENVIRONMENT == "testing":
    # Configurações específicas para testes
    DB_CONFIG["database"] = "sippulse_reports_test"
    FLASK_CONFIG["debug"] = True

# === EXPORTAÇÃO DAS CONFIGURAÇÕES ===
__all__ = [
    'SSH_CONFIG',
    'DB_CONFIG', 
    'FLASK_CONFIG',
    'LOG_CONFIG',
    'DASHBOARD_CONFIG',
    'CRON_CONFIG',
    'SECURITY_CONFIG',
    'EMAIL_CONFIG',
    'BACKUP_CONFIG',
    'get_db_connection_string',
    'get_cron_command',
    'create_directories',
    'validate_config'
] 