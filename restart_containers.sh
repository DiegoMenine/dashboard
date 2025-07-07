#!/bin/bash

echo "🔄 Reiniciando containers com novas configurações..."

# Parar containers
echo "⏹️ Parando containers..."
docker-compose down

# Remover volume do MySQL para limpar dados antigos
echo "🧹 Removendo dados antigos do MySQL..."
docker volume rm dashboard_mysql_data

# Reconstruir e subir containers
echo "🚀 Reconstruindo e subindo containers..."
docker-compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 30

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

# Aguardar mais um pouco e testar conectividade
echo "⏳ Aguardando mais tempo para inicialização completa..."
sleep 30

echo "🔍 Testando conectividade..."
if curl -f http://localhost:5000/api/overview > /dev/null 2>&1; then
    echo "✅ Dashboard está funcionando!"
else
    echo "⚠️ Dashboard pode não estar pronto ainda"
    echo "📝 Verificando logs..."
    docker-compose logs dashboard
fi 