# Dockerfile para Dashboard VoIP
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    cron \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -s /bin/bash voipuser && \
    mkdir -p /opt/voip_import /var/log/voip_dashboard /opt/voip_backups && \
    chown -R voipuser:voipuser /opt/voip_import /var/log/voip_dashboard /opt/voip_backups

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/static /app/templates /var/log/voip_dashboard /opt/voip_import /opt/voip_backups

# Configurar permissões
RUN chown -R voipuser:voipuser /app /var/log/voip_dashboard /opt/voip_import /opt/voip_backups && \
    chmod +x /app/start_dashboard.sh

# Expor porta
EXPOSE 5000

# Mudar para usuário não-root
USER voipuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/overview || exit 1

# Comando padrão
CMD ["python", "app.py"] 