CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO users (username, email, password_hash) VALUES (
    'DALVIZURESO', 'dalvizureso@sistema.com', '$2b$12$2jHvdvI3bbqxkreBt.yjH.TANIeB67GTbf0aQHKopav9ZX5TJyu22'
) ON CONFLICT DO NOTHING;

INSERT INTO users (username, email, password_hash) VALUES (
    'KMEYERT', 'kmeyert@sistema.com', '$2b$12$2jHvdvI3bbqxkreBt.yjH.TANIeB67GTbf0aQHKopav9ZX5TJyu22'
) ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS registros (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(20) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    conductor VARCHAR(100) NOT NULL,
    motivo VARCHAR(200) NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);