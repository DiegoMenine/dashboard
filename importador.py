import paramiko
import os
import tarfile
import datetime
import mysql.connector
from pathlib import Path

# === CONFIGURAÇÕES ===
SSH_HOST = os.getenv("SSH_HOST", "200.159.177.191")
SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASS = os.getenv("SSH_PASS", "Tel1YccR^oOZjJ4")
REMOTE_DIR = "/srv/backups/voip-reports/"
LOCAL_DIR = "/opt/voip_import/"
DB_CONFIG = {
    "host": "mysql",  # Nome do container MySQL no docker-compose
    "user": "root",
    "password": os.getenv("MYSQL_ROOT_PASSWORD", "voip123456"),
    "database": "sippulse_reports"
}

# === CRIAR DIRETÓRIOS SE NECESSÁRIO ===
Path(LOCAL_DIR).mkdir(parents=True, exist_ok=True)

# === CALCULAR DATA DE ONTEM ===
ontem = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
file_name = f"REPORTS-INCREMENTAL-{ontem}.tar.gz"

# === CONECTAR E BAIXAR ARQUIVO REMOTO ===
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS)

sftp = ssh.open_sftp()
remote_path = os.path.join(REMOTE_DIR, file_name)
local_path = os.path.join(LOCAL_DIR, file_name)
try:
    sftp.get(remote_path, local_path)
    print(f"[✔] Arquivo {file_name} baixado com sucesso.")
except Exception as e:
    print(f"[✖] Erro ao baixar arquivo: {e}")
    sftp.close()
    ssh.close()
    exit(1)

sftp.close()
ssh.close()

# === EXTRAIR ARQUIVO ===
with tarfile.open(local_path, "r:gz") as tar:
    tar.extractall(path=LOCAL_DIR)

# === LOCALIZAR ARQUIVO .SQL ===
sql_file = next(Path(LOCAL_DIR).rglob("*.sql"), None)
if not sql_file:
    print("[✖] Nenhum arquivo .sql encontrado.")
    exit(1)

# === IMPORTAR DADOS PARA MYSQL ===
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

with open(sql_file, "r", encoding="utf-8", errors="ignore") as f:
    sql_lines = f.read()

try:
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    for stmt in sql_lines.split(";"):
        if stmt.strip().startswith("INSERT INTO"):
            cursor.execute(stmt + ";")
    conn.commit()
    print("[✔] Dados importados com sucesso.")
except Exception as e:
    print(f"[✖] Erro ao importar dados: {e}")
    conn.rollback()

cursor.close()
conn.close() 