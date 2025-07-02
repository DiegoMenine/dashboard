-- Script de configuração do banco de dados para Dashboard VoIP
-- Execute este script no MySQL para criar a estrutura necessária

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS sippulse_reports CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar o banco de dados
USE sippulse_reports;

-- Criar tabela acc_report
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
    
    -- Índices para melhor performance
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Criar usuário específico para o dashboard (opcional, por segurança)
-- CREATE USER 'voip_dashboard'@'localhost' IDENTIFIED BY 'senha_segura_aqui';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sippulse_reports.* TO 'voip_dashboard'@'localhost';
-- FLUSH PRIVILEGES;

-- Inserir dados de exemplo (opcional, para testes)
INSERT INTO acc_report (
    id, method, call_id, direction, sip_call_id, status_code, status_desc,
    time, dst_uri, src_uri, caller_id, caller_domain, profile, src_ip,
    src_port, dst_ip, user_agent, to_user, callee_id, gateway_ip,
    duration, service, rateplan, cost, direction_type, accountcode
) VALUES 
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
 'SIPp/1.0', '5511999999997', '5511999999997', '10.0.0.1', 180, 'pstn', 'provider2', 0.25, 'outbound', 'client002'),

(4, 'INVITE', 'call_004', 'outbound', 'sip_call_004', '486', 'Busy Here',
 '2024-01-15 11:15:00', 'sip:5511999999996@provider.com', 'sip:5511666666666@domain.com',
 '5511666666666', 'domain.com', 'default', '192.168.1.102', '5060', '10.0.0.1',
 'SIPp/1.0', '5511999999996', '5511999999996', '10.0.0.1', 0, 'pstn', 'provider1', 0.00, 'outbound', 'client003'),

(5, 'INVITE', 'call_005', 'outbound', 'sip_call_005', '200', 'OK',
 '2024-01-15 12:00:00', 'sip:5511999999995@provider.com', 'sip:5511555555555@domain.com',
 '5511555555555', 'domain.com', 'default', '192.168.1.103', '5060', '10.0.0.1',
 'SIPp/1.0', '5511999999995', '5511999999995', '10.0.0.1', 300, 'pstn', 'provider3', 0.40, 'outbound', 'client001');

-- Verificar se a tabela foi criada corretamente
SELECT COUNT(*) as total_registros FROM acc_report;

-- Mostrar estrutura da tabela
DESCRIBE acc_report; 