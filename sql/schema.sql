-- =========================================
-- Network Monitoring & Analysis Toolkit
-- Schema de base de datos
-- =========================================

-- Tabla de hosts monitoreados
CREATE TABLE hosts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de chequeos de conectividad
CREATE TABLE checks (
    id SERIAL PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id),
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL,
    latency_ms NUMERIC(10,2),
    error_message TEXT
);

-- Tabla de incidentes
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN'
);

-- Hosts de prueba
INSERT INTO hosts (name, address) VALUES
('Google DNS', '8.8.8.8'),
('Cloudflare DNS', '1.1.1.1'),
('Router Local', '192.168.1.1'),
('Host Inexistente', '10.255.255.1');