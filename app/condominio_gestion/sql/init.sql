-- =============================================
-- SCRIPT DE INICIALIZACIÓN - GESTIÓN DE CONDOMINIOS
-- =============================================

-- =============================================
-- DROP TABLES (orden inverso a dependencias)
-- =============================================
DROP TABLE IF EXISTS activo CASCADE;
DROP TABLE IF EXISTS activo_tipo CASCADE;
DROP TABLE IF EXISTS espacio CASCADE;
DROP TABLE IF EXISTS condominio CASCADE;

-- Tabla: condominio
CREATE TABLE IF NOT EXISTS condominio (
    condominio_id SERIAL PRIMARY KEY,
    condominio_nombre VARCHAR(100) NOT NULL,
    condominio_descripcion TEXT,
    condominio_ubicacion TEXT,
    condominio_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: espacio
CREATE TABLE IF NOT EXISTS espacio (
    espacio_id SERIAL PRIMARY KEY,
    condominio_id INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    espacio_nombre VARCHAR(100) NOT NULL,
    espacio_descripcion TEXT,
    ubicacion_fisica TEXT,
    espacio_disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_espacio_condominio ON espacio(condominio_id);

-- Tabla: activo_tipo (catálogo)
CREATE TABLE IF NOT EXISTS activo_tipo (
    activo_tipo_code VARCHAR(50) PRIMARY KEY,
    activo_tipo_nombre VARCHAR(100) NOT NULL,
    activo_tipo_descripcion TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: activo
CREATE TABLE IF NOT EXISTS activo (
    activo_id SERIAL PRIMARY KEY,
    condominio_id INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    espacio_id INTEGER REFERENCES espacio(espacio_id) ON DELETE SET NULL,
    activo_tipo_code VARCHAR(50) REFERENCES activo_tipo(activo_tipo_code) ON DELETE SET NULL,
    activo_nombre VARCHAR(200) NOT NULL,
    activo_marca VARCHAR(100),
    activo_modelo VARCHAR(100),
    activo_numero_serie VARCHAR(100) UNIQUE,
    activo_estado VARCHAR(50) DEFAULT 'ACTIVO' CHECK (activo_estado IN ('ACTIVO', 'INACTIVO', 'EN_MANTENIMIENTO')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activo_condominio ON activo(condominio_id);
CREATE INDEX IF NOT EXISTS idx_activo_espacio ON activo(espacio_id);
CREATE INDEX IF NOT EXISTS idx_activo_tipo ON activo(activo_tipo_code);

-- =============================================
-- PERMISOS
-- =============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO citiouser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO citiouser;

-- =============================================
-- DATOS INICIALES
-- =============================================

-- Tipos de activos (catálogo)
INSERT INTO activo_tipo(activo_tipo_code, activo_tipo_nombre, activo_tipo_descripcion, created_at) VALUES
  ('CCTV', 'Seguridad y Vigilancia', 'Monitorización de cámaras de seguridad', CURRENT_TIMESTAMP),
  ('CLIMATIZACION', 'Climatización', 'Control y monitorización de sistemas de climatización', CURRENT_TIMESTAMP),
  ('ACCESO', 'Control de Acceso', 'Sistemas de control de acceso y portones', CURRENT_TIMESTAMP),
  ('ILUMINACION', 'Iluminación', 'Sistemas de iluminación de áreas comunes', CURRENT_TIMESTAMP),
  ('ASCENSOR', 'Ascensores', 'Ascensores y elevadores', CURRENT_TIMESTAMP);

