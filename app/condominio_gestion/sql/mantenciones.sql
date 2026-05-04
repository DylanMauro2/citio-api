-- =============================================
-- SCRIPT DE MANTENCIONES
-- =============================================

-- =============================================
-- DROP TABLES (orden inverso a dependencias)
-- =============================================
DROP TABLE IF EXISTS mantencion_programada CASCADE;
DROP TABLE IF EXISTS mantencion CASCADE;
DROP TABLE IF EXISTS mantencion_estado CASCADE;
DROP TABLE IF EXISTS mantencion_proveedor CASCADE;

-- Tabla: mantencion_proveedor
CREATE TABLE IF NOT EXISTS mantencion_proveedor (
    mantencion_proveedor_id SERIAL PRIMARY KEY,
    mantencion_proveedor_nombre TEXT NOT NULL,
    mantencion_proveedor_rut TEXT,
    mantencion_proveedor_activo BOOLEAN NOT NULL DEFAULT TRUE,
    mantencion_proveedor_telefono TEXT,
    mantencion_proveedor_email TEXT,
    mantencion_proveedor_administrador TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: mantencion_estado (catálogo)
CREATE TABLE IF NOT EXISTS mantencion_estado (
    mantencion_estado_code VARCHAR(50) PRIMARY KEY,
    mantencion_estado_nombre VARCHAR(100) NOT NULL,
    mantencion_estado_descripcion TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: mantencion
CREATE TABLE IF NOT EXISTS mantencion (
    mantencion_id SERIAL PRIMARY KEY,
    activo_id INTEGER NOT NULL REFERENCES activo(activo_id) ON DELETE CASCADE,
    mantencion_proveedor_id INTEGER REFERENCES mantencion_proveedor(mantencion_proveedor_id) ON DELETE SET NULL,
    mantencion_estado_code VARCHAR(50) REFERENCES mantencion_estado(mantencion_estado_code) ON DELETE SET NULL,
    mantencion_tipo VARCHAR(50) CHECK (mantencion_tipo IN ('PREVENTIVA', 'CORRECTIVA', 'EMERGENCIA')),
    mantencion_descripcion TEXT,
    mantencion_fecha_realizacion DATE,
    mantencion_hora TEXT,
    mantencion_tecnico_nombre TEXT,
    mantencion_tecnico_rut TEXT,
    mantencion_tecnico_telefono TEXT,
    mantencion_tecnico_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mantencion_activo ON mantencion(activo_id);
CREATE INDEX IF NOT EXISTS idx_mantencion_proveedor ON mantencion(mantencion_proveedor_id);

-- Tabla: mantencion_programada
-- Tabla liviana para uso en calendario. Al crear un registro aquí
-- se debe crear primero la mantencion correspondiente con todos sus detalles.
CREATE TABLE IF NOT EXISTS mantencion_programada (
    mantencion_programada_id SERIAL PRIMARY KEY,
    mantencion_id INTEGER NOT NULL REFERENCES mantencion(mantencion_id) ON DELETE CASCADE,
    mantencion_programada_fecha DATE NOT NULL,
    mantencion_programada_descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mt_programada_mantencion ON mantencion_programada(mantencion_id);

-- =============================================
-- DATOS INICIALES
-- =============================================

INSERT INTO mantencion_estado (mantencion_estado_code, mantencion_estado_nombre, mantencion_estado_descripcion, created_at, updated_at) VALUES
  ('PENDIENTE', 'Pendiente', 'Mantención pendiente de realizarse', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('REALIZADA', 'Realizada', 'Mantención realizada con éxito', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('CANCELADA', 'Cancelada', 'Mantención cancelada por algún motivo', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('ATRASADA', 'Atrasada', 'Mantención atrasada', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
