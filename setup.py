#!/usr/bin/env python3
"""
Script de setup para o Dashboard VoIP
Este script automatiza a instalação e configuração do sistema
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

def print_banner():
    """Exibe o banner do sistema"""
    print("=" * 60)
    print("    🎯 DASHBOARD VOIP - SETUP AUTOMATIZADO")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário")
        sys.exit(1)
    print("✅ Python", sys.version.split()[0], "detectado")

def install_dependencies():
    """Instala as dependências Python"""
    print("📦 Instalando dependências Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)

def create_directories():
    """Cria diretórios necessários"""
    print("📁 Criando diretórios...")
    directories = [
        "/opt/voip_import",
        "/var/log/voip_dashboard"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Diretório {directory} criado/verificado")
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível criar {directory}: {e}")

def setup_database():
    """Configura o banco de dados"""
    print("🗄️  Configurando banco de dados...")
    
    # Solicitar credenciais do MySQL
    print("Por favor, informe as credenciais do MySQL:")
    host = input("Host (localhost): ").strip() or "localhost"
    user = input("Usuário (root): ").strip() or "root"
    password = input("Senha: ").strip()
    database = "sippulse_reports"
    
    try:
        # Conectar ao MySQL
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Criar banco de dados
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Banco de dados '{database}' criado/verificado")
        
        # Usar o banco
        cursor.execute(f"USE {database}")
        
        # Criar tabela
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS acc_report (
            id BIGINT PRIMARY KEY,
            method VARCHAR(10),
            call_id VARCHAR(64),
            direction VARCHAR(64),
            sip_call_id VARCHAR(128),
            status_code VARCHAR(8),
            status_desc VARCHAR(64),
            time DATETIME,
            dst_uri VARCHAR(255),
            src_uri VARCHAR(255),
            caller_id VARCHAR(64),
            caller_domain VARCHAR(64),
            profile VARCHAR(64),
            src_ip VARCHAR(64),
            src_port VARCHAR(10),
            dst_ip VARCHAR(64),
            user_agent VARCHAR(128),
            to_user VARCHAR(64),
            callee_id VARCHAR(64),
            gateway_ip VARCHAR(64),
            duration INT,
            service VARCHAR(32),
            rateplan VARCHAR(64),
            cost FLOAT,
            direction_type VARCHAR(32),
            accountcode VARCHAR(64),
            INDEX idx_time (time),
            INDEX idx_caller_id (caller_id),
            INDEX idx_callee_id (callee_id),
            INDEX idx_status_code (status_code),
            INDEX idx_accountcode (accountcode),
            INDEX idx_rateplan (rateplan),
            INDEX idx_service (service),
            INDEX idx_time_status (time, status_code),
            INDEX idx_caller_time (caller_id, time),
            INDEX idx_callee_time (callee_id, time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        print("✅ Tabela 'acc_report' criada/verificada")
        
        # Inserir dados de exemplo
        insert_sample_data(cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Atualizar configuração do app.py
        update_app_config(host, user, password, database)
        
        print("✅ Banco de dados configurado com sucesso")
        
    except mysql.connector.Error as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        sys.exit(1)

def insert_sample_data(cursor):
    """Insere dados de exemplo para testes"""
    print("📊 Inserindo dados de exemplo...")
    
    sample_data = [
        (1, 'INVITE', 'call_001', 'outbound', 'sip_call_001', '200', 'OK',
         '2024-01-15 10:30:00', 'sip:5511999999999@provider.com', 'sip:5511888888888@domain.com',
         '5511888888888', 'domain.com', 'default', '192.168.1.100', '5060', '10.0.0.1',
         'SIPp/1.0', '5511999999999', '5511999999999', '10.0.0.1', 120, 'pstn', 'provider1', 0.15, 'outbound', 'client001'),
        
        (2, 'INVITE', 'call_002', 'outbound', 'sip_call_002', '404', 'Not Found',
         '2024-01-15 10:35:00', 'sip:5511999999998@provider.com', 'sip:5511888888888@domain.com',
         '5511888888888', 'domain.com', 'default', '192.168.1.100', '5060', '10.0.0.1',
         'SIPp/1.0', '5511999999998', '5511999999998', '10.0.0.1', 0, 'pstn', 'provider1', 0.00, 'outbound', 'client001'),
        
        (3, 'INVITE', 'call_003', 'outbound', 'sip_call_003', '200', 'OK',
         '2024-01-15 11:00:00', 'sip:5511999999997@provider.com', 'sip:5511777777777@domain.com',
         '5511777777777', 'domain.com', 'default', '192.168.1.101', '5060', '10.0.0.1',
         'SIPp/1.0', '5511999999997', '5511999999997', '10.0.0.1', 180, 'pstn', 'provider2', 0.25, 'outbound', 'client002')
    ]
    
    insert_sql = """
    INSERT IGNORE INTO acc_report (
        id, method, call_id, direction, sip_call_id, status_code, status_desc,
        time, dst_uri, src_uri, caller_id, caller_domain, profile, src_ip,
        src_port, dst_ip, user_agent, to_user, callee_id, gateway_ip,
        duration, service, rateplan, cost, direction_type, accountcode
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.executemany(insert_sql, sample_data)
    print("✅ Dados de exemplo inseridos")

def update_app_config(host, user, password, database):
    """Atualiza a configuração do banco no app.py"""
    print("⚙️  Atualizando configuração do aplicativo...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualizar configuração do banco
        new_config = f'''# Configuração do banco de dados
DB_CONFIG = {{
    "host": "{host}",
    "user": "{user}",
    "password": "{password}",
    "database": "{database}"
}}'''
        
        # Substituir a configuração existente
        import re
        pattern = r'DB_CONFIG = \{[^}]*\}'
        content = re.sub(pattern, new_config, content)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Configuração do aplicativo atualizada")
        
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível atualizar app.py: {e}")

def setup_cron_job():
    """Configura o cron job para importação automática"""
    print("⏰ Configurando cron job...")
    
    cron_command = "0 2 * * * /usr/bin/python3 /opt/voip_import/importador.py >> /var/log/importador_voip.log 2>&1"
    
    print("Para configurar o cron job automaticamente, execute:")
    print(f"crontab -e")
    print("E adicione a linha:")
    print(f"{cron_command}")
    print()
    
    # Tentar adicionar automaticamente (opcional)
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        if cron_command not in current_cron:
            new_cron = current_cron + cron_command + '\n'
            subprocess.run(['crontab', '-'], input=new_cron, text=True)
            print("✅ Cron job configurado automaticamente")
        else:
            print("✅ Cron job já configurado")
    except Exception as e:
        print(f"⚠️  Aviso: Configure o cron job manualmente: {e}")

def create_startup_script():
    """Cria script de inicialização"""
    print("🚀 Criando script de inicialização...")
    
    startup_script = """#!/bin/bash
# Script de inicialização do Dashboard VoIP

cd "$(dirname "$0")"

echo "🎯 Iniciando Dashboard VoIP..."
echo "📊 Acesse: http://localhost:5000"
echo "⏹️  Para parar: Ctrl+C"
echo

python3 app.py
"""
    
    try:
        with open('start_dashboard.sh', 'w') as f:
            f.write(startup_script)
        
        # Tornar executável
        os.chmod('start_dashboard.sh', 0o755)
        print("✅ Script de inicialização criado: start_dashboard.sh")
        
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível criar script de inicialização: {e}")

def main():
    """Função principal"""
    print_banner()
    
    print("🔍 Verificando requisitos...")
    check_python_version()
    print()
    
    print("📦 Instalando dependências...")
    install_dependencies()
    print()
    
    print("📁 Criando estrutura de diretórios...")
    create_directories()
    print()
    
    print("🗄️  Configurando banco de dados...")
    setup_database()
    print()
    
    print("⏰ Configurando automação...")
    setup_cron_job()
    print()
    
    print("🚀 Criando scripts de inicialização...")
    create_startup_script()
    print()
    
    print("=" * 60)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("🎯 Para iniciar o dashboard:")
    print("   ./start_dashboard.sh")
    print()
    print("📊 Acesse: http://localhost:5000")
    print()
    print("📋 Próximos passos:")
    print("   1. Configure as credenciais SSH no importador.py")
    print("   2. Teste a importação manual: python3 importador.py")
    print("   3. Verifique os logs: tail -f /var/log/importador_voip.log")
    print()
    print("🔧 Para suporte, consulte o README.md")
    print("=" * 60)

if __name__ == "__main__":
    main() 