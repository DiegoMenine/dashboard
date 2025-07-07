from flask import Flask, render_template, jsonify, request
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import json
from collections import defaultdict
import logging

app = Flask(__name__)

# Configuração do banco de dados
DB_CONFIG = {
    "host": "mysql",  # Nome do container MySQL no docker-compose
    "user": "root",
    "password": "voip123456",  # Senha definida no .env
    "database": "sippulse_reports"
}

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Cria conexão com o banco de dados"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/overview')
def get_overview():
    """Dados gerais do dashboard"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com banco"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Data de hoje e ontem
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        
        # Total de chamadas hoje
        cursor.execute("""
            SELECT COUNT(*) as total_chamadas_hoje,
                   COUNT(CASE WHEN status_code = '200' THEN 1 END) as chamadas_sucesso,
                   COUNT(CASE WHEN status_code LIKE '4%' OR status_code LIKE '5%' THEN 1 END) as chamadas_erro,
                   AVG(duration) as duracao_media,
                   SUM(cost) as custo_total
            FROM acc_report 
            WHERE DATE(time) = %s
        """, (hoje,))
        hoje_stats = cursor.fetchone()
        
        # Total de chamadas ontem
        cursor.execute("""
            SELECT COUNT(*) as total_chamadas_ontem
            FROM acc_report 
            WHERE DATE(time) = %s
        """, (ontem,))
        ontem_stats = cursor.fetchone()
        
        # Variação percentual
        if ontem_stats['total_chamadas_ontem'] > 0:
            variacao = ((hoje_stats['total_chamadas_hoje'] - ontem_stats['total_chamadas_ontem']) / 
                       ontem_stats['total_chamadas_ontem']) * 100
        else:
            variacao = 0
        
        # Top 5 callers
        cursor.execute("""
            SELECT caller_id, COUNT(*) as total_chamadas, SUM(duration) as duracao_total
            FROM acc_report 
            WHERE DATE(time) = %s
            GROUP BY caller_id 
            ORDER BY total_chamadas DESC 
            LIMIT 5
        """, (hoje,))
        top_callers = cursor.fetchall()
        
        # Top 5 callees
        cursor.execute("""
            SELECT callee_id, COUNT(*) as total_chamadas
            FROM acc_report 
            WHERE DATE(time) = %s
            GROUP BY callee_id 
            ORDER BY total_chamadas DESC 
            LIMIT 5
        """, (hoje,))
        top_callees = cursor.fetchall()
        
        # Distribuição por status
        cursor.execute("""
            SELECT status_code, COUNT(*) as total
            FROM acc_report 
            WHERE DATE(time) = %s
            GROUP BY status_code 
            ORDER BY total DESC
        """, (hoje,))
        status_distribution = cursor.fetchall()
        
        return jsonify({
            "hoje": hoje_stats,
            "variacao": round(variacao, 2),
            "top_callers": top_callers,
            "top_callees": top_callees,
            "status_distribution": status_distribution
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados gerais: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/chart-data')
def get_chart_data():
    """Dados para gráficos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com banco"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Parâmetros de filtro
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Dados para gráfico de linha (chamadas por dia)
        cursor.execute("""
            SELECT DATE(time) as data, 
                   COUNT(*) as total_chamadas,
                   COUNT(CASE WHEN status_code = '200' THEN 1 END) as chamadas_sucesso,
                   COUNT(CASE WHEN status_code LIKE '4%' OR status_code LIKE '5%' THEN 1 END) as chamadas_erro,
                   AVG(duration) as duracao_media,
                   SUM(cost) as custo_total
            FROM acc_report 
            WHERE DATE(time) BETWEEN %s AND %s
            GROUP BY DATE(time)
            ORDER BY data
        """, (start_date, end_date))
        daily_data = cursor.fetchall()
        
        # Dados para gráfico de pizza (distribuição por provider)
        cursor.execute("""
            SELECT rateplan, COUNT(*) as total
            FROM acc_report 
            WHERE DATE(time) BETWEEN %s AND %s
            GROUP BY rateplan 
            ORDER BY total DESC
        """, (start_date, end_date))
        provider_data = cursor.fetchall()
        
        # Dados para gráfico de pizza (distribuição por serviço)
        cursor.execute("""
            SELECT service, COUNT(*) as total
            FROM acc_report 
            WHERE DATE(time) BETWEEN %s AND %s
            GROUP BY service 
            ORDER BY total DESC
        """, (start_date, end_date))
        service_data = cursor.fetchall()
        
        return jsonify({
            "daily_data": daily_data,
            "provider_data": provider_data,
            "service_data": service_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados dos gráficos: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/calls-table')
def get_calls_table():
    """Dados para tabela de chamadas"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com banco"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Parâmetros de filtro
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        caller_id = request.args.get('caller_id', '')
        callee_id = request.args.get('callee_id', '')
        status_code = request.args.get('status_code', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page
        
        # Construir query com filtros
        where_conditions = ["DATE(time) BETWEEN %s AND %s"]
        params = [start_date, end_date]
        
        if caller_id:
            where_conditions.append("caller_id LIKE %s")
            params.append(f"%{caller_id}%")
        
        if callee_id:
            where_conditions.append("callee_id LIKE %s")
            params.append(f"%{callee_id}%")
        
        if status_code:
            where_conditions.append("status_code = %s")
            params.append(status_code)
        
        where_clause = " AND ".join(where_conditions)
        
        # Query para dados
        query = f"""
            SELECT id, method, call_id, status_code, status_desc, time, 
                   caller_id, callee_id, duration, cost, service, rateplan, accountcode
            FROM acc_report 
            WHERE {where_clause}
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        calls = cursor.fetchall()
        
        # Query para total de registros
        count_query = f"""
            SELECT COUNT(*) as total
            FROM acc_report 
            WHERE {where_clause}
        """
        cursor.execute(count_query, params[:-2])
        total = cursor.fetchone()['total']
        
        return jsonify({
            "calls": calls,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados da tabela: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/insights')
def get_insights():
    """Insights inteligentes"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com banco"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        
        # Análise de volume de chamadas (últimos 7 dias)
        cursor.execute("""
            SELECT DATE(time) as data, COUNT(*) as total_chamadas
            FROM acc_report 
            WHERE DATE(time) >= DATE_SUB(%s, INTERVAL 7 DAY)
            GROUP BY DATE(time)
            ORDER BY data
        """, (hoje,))
        volume_data = cursor.fetchall()
        
        # Calcular média e detectar anomalias
        if volume_data:
            volumes = [row['total_chamadas'] for row in volume_data]
            media = sum(volumes) / len(volumes)
            desvio = (sum((x - media) ** 2 for x in volumes) / len(volumes)) ** 0.5
            
            anomalias = []
            for row in volume_data:
                if abs(row['total_chamadas'] - media) > 2 * desvio:
                    anomalias.append({
                        'data': row['data'].strftime('%Y-%m-%d'),
                        'volume': row['total_chamadas'],
                        'media': round(media, 0),
                        'tipo': 'Alto' if row['total_chamadas'] > media else 'Baixo'
                    })
        
        # Taxa de erro hoje
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN status_code LIKE '4%' OR status_code LIKE '5%' THEN 1 END) as erros
            FROM acc_report 
            WHERE DATE(time) = %s
        """, (hoje,))
        erro_stats = cursor.fetchone()
        
        taxa_erro = (erro_stats['erros'] / erro_stats['total'] * 100) if erro_stats['total'] > 0 else 0
        
        # Alertas
        alertas = []
        if taxa_erro > 10:
            alertas.append({
                'tipo': 'erro',
                'mensagem': f'Taxa de erro alta: {taxa_erro:.1f}% das chamadas com erro'
            })
        
        if anomalias:
            alertas.append({
                'tipo': 'volume',
                'mensagem': f'Detectadas {len(anomalias)} anomalias no volume de chamadas'
            })
        
        return jsonify({
            "anomalias": anomalias if 'anomalias' in locals() else [],
            "taxa_erro": round(taxa_erro, 1),
            "alertas": alertas
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar insights: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 