#!/bin/bash

# Script para testar build do Docker
echo "🧪 Testando build do Docker..."

# Limpar containers e imagens antigas
echo "🧹 Limpando containers antigos..."
docker-compose down
docker system prune -f

# Testar build
echo "🔨 Testando build..."
docker-compose build --no-cache

# Verificar se o build foi bem-sucedido
if [ $? -eq 0 ]; then
    echo "✅ Build realizado com sucesso!"
    
    # Testar subida dos containers
    echo "🚀 Testando subida dos containers..."
    docker-compose up -d
    
    # Aguardar um pouco
    sleep 10
    
    # Verificar status
    echo "📊 Status dos containers:"
    docker-compose ps
    
    # Testar conectividade
    echo "🔍 Testando conectividade..."
    if curl -f http://localhost:5000/api/overview > /dev/null 2>&1; then
        echo "✅ Dashboard está funcionando!"
    else
        echo "⚠️ Dashboard pode não estar pronto ainda"
    fi
    
else
    echo "❌ Erro no build!"
    exit 1
fi 