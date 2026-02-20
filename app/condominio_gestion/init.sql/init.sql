-- =============================================
-- SCRIPT DE INICIALIZACIÓN - GESTIÓN DE CONDOMINIOS
-- =============================================

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


-- Tablas de mantención
CREATE TABLE IF NOT EXISTS mantencion_estado (
    mantencion_estado_code VARCHAR(50) PRIMARY KEY,
    mantencion_estado_nombre VARCHAR(100) NOT NULL,
    mantencion_estado_descripcion TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mantencion (
    mantencion_id SERIAL PRIMARY KEY,
    activo_id INTEGER NOT NULL REFERENCES activo(activo_id) ON DELETE CASCADE,
    mantencion_estado_code VARCHAR(50) REFERENCES mantencion_estado(mantencion_estado_code) ON DELETE SET NULL,
    mantencion_tipo VARCHAR(50) CHECK (mantencion_tipo IN ('PREVENTIVA', 'CORRECTIVA', 'EMERGENCIA')),
    mantencion_descripcion TEXT,
    mantencion_fecha_realizacion DATE,
    mantencion_costo DECIMAL(12, 2),
    mantencion_realizada_por VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mantencion_activo ON mantencion(activo_id);

CREATE TABLE IF NOT EXISTS mantencion_programada (
    mantencion_programada_id SERIAL PRIMARY KEY,
    activo_id INTEGER NOT NULL REFERENCES activo(activo_id) ON DELETE CASCADE,
    mantencion_estado_code VARCHAR(50) REFERENCES mantencion_estado(mantencion_estado_code) ON DELETE SET NULL,
    mantencion_programada_descripcion TEXT NOT NULL,
    mantencion_programada_fecha DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mt_programada_activo ON mantencion_programada(activo_id);

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

INSERT INTO mantencion_estado(mantencion_estado_code, mantencion_estado_nombre, mantencion_estado_descripcion, created_at) VALUES
  ('PENDIENTE', 'Pendiente', 'Mantención pendiente de realizarse', CURRENT_TIMESTAMP),
  ('REALIZADA', 'Realizada', 'Mantención realizada con éxito', CURRENT_TIMESTAMP),
  ('CANCELADA', 'Cancelada', 'Mantención cancelada por algún motivo', CURRENT_TIMESTAMP),
  ('ATRASADA', 'Atrasada', 'Mantención atrasada', CURRENT_TIMESTAMP);