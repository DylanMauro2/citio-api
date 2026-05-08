-- =============================================
-- SCRIPT DE FINANZAS Y GASTOS COMUNES
-- Ley N° 21442 — Obligación de cobro y rendición
-- =============================================

-- =============================================
-- DROP TABLES (orden inverso a dependencias)
-- =============================================
DROP TABLE IF EXISTS corte_suministro CASCADE;
DROP TABLE IF EXISTS registro_morosidad CASCADE;
DROP TABLE IF EXISTS pago CASCADE;
DROP TABLE IF EXISTS cuota_unidad CASCADE;
DROP TABLE IF EXISTS periodo_cobro CASCADE;
DROP TABLE IF EXISTS item_presupuesto CASCADE;
DROP TABLE IF EXISTS presupuesto CASCADE;
DROP TABLE IF EXISTS movimiento_fondo CASCADE;

-- Tabla: presupuesto
-- Presupuesto anual aprobado por asamblea. Solo uno activo por condominio/año.
CREATE TABLE IF NOT EXISTS presupuesto (
    presupuesto_id              SERIAL PRIMARY KEY,
    condominio_id               INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    presupuesto_anio            INTEGER NOT NULL,
    presupuesto_monto_total     NUMERIC(14, 2) NOT NULL DEFAULT 0,
    presupuesto_aprobado        BOOLEAN NOT NULL DEFAULT FALSE,
    presupuesto_fecha_aprobacion DATE,
    presupuesto_activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_presupuesto_condominio_anio UNIQUE (condominio_id, presupuesto_anio)
);

CREATE INDEX IF NOT EXISTS idx_presupuesto_condominio ON presupuesto(condominio_id);

-- Tabla: item_presupuesto
-- Líneas de detalle del presupuesto por concepto.
CREATE TABLE IF NOT EXISTS item_presupuesto (
    item_id             SERIAL PRIMARY KEY,
    presupuesto_id      INTEGER NOT NULL REFERENCES presupuesto(presupuesto_id) ON DELETE CASCADE,
    item_concepto       VARCHAR(200) NOT NULL,
    item_tipo           VARCHAR(20) NOT NULL DEFAULT 'ORDINARIO'
                            CHECK (item_tipo IN ('ORDINARIO', 'EXTRAORDINARIO')),
    item_monto_mensual  NUMERIC(14, 2) NOT NULL DEFAULT 0,
    item_descripcion    TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_item_presupuesto ON item_presupuesto(presupuesto_id);

-- Tabla: periodo_cobro
-- Período mensual de cobro (mes/año). Eje central del módulo de finanzas.
CREATE TABLE IF NOT EXISTS periodo_cobro (
    periodo_id              SERIAL PRIMARY KEY,
    condominio_id           INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    presupuesto_id          INTEGER REFERENCES presupuesto(presupuesto_id) ON DELETE SET NULL,
    periodo_mes             INTEGER NOT NULL CHECK (periodo_mes BETWEEN 1 AND 12),
    periodo_anio            INTEGER NOT NULL,
    periodo_fecha_vencimiento DATE NOT NULL,
    periodo_cerrado         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_periodo_condominio_mes_anio UNIQUE (condominio_id, periodo_mes, periodo_anio)
);

CREATE INDEX IF NOT EXISTS idx_periodo_condominio ON periodo_cobro(condominio_id);

-- Tabla: cuota_unidad
-- Cuota prorrateada para cada unidad en un período de cobro.
CREATE TABLE IF NOT EXISTS cuota_unidad (
    cuota_id                    SERIAL PRIMARY KEY,
    periodo_id                  INTEGER NOT NULL REFERENCES periodo_cobro(periodo_id) ON DELETE CASCADE,
    unidad_id                   INTEGER NOT NULL REFERENCES unidad(unidad_id) ON DELETE CASCADE,
    cuota_monto_ordinario       NUMERIC(14, 2) NOT NULL DEFAULT 0,
    cuota_monto_extraordinario  NUMERIC(14, 2) NOT NULL DEFAULT 0,
    cuota_interes_mora          NUMERIC(14, 2) NOT NULL DEFAULT 0,
    cuota_saldo_pendiente       NUMERIC(14, 2) NOT NULL DEFAULT 0,
    cuota_pagada                BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cuota_periodo_unidad UNIQUE (periodo_id, unidad_id)
);

CREATE INDEX IF NOT EXISTS idx_cuota_periodo   ON cuota_unidad(periodo_id);
CREATE INDEX IF NOT EXISTS idx_cuota_unidad    ON cuota_unidad(unidad_id);

-- Tabla: pago
-- Abono concreto realizado por una unidad sobre su cuota.
CREATE TABLE IF NOT EXISTS pago (
    pago_id             SERIAL PRIMARY KEY,
    cuota_id            INTEGER NOT NULL REFERENCES cuota_unidad(cuota_id) ON DELETE CASCADE,
    pago_fecha          DATE NOT NULL,
    pago_monto          NUMERIC(14, 2) NOT NULL,
    pago_medio          VARCHAR(20) NOT NULL DEFAULT 'TRANSFERENCIA'
                            CHECK (pago_medio IN ('TRANSFERENCIA', 'EFECTIVO', 'CHEQUE', 'OTRO')),
    pago_referencia     VARCHAR(200),
    pago_registrado_por VARCHAR(200),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pago_cuota ON pago(cuota_id);

-- Tabla: movimiento_fondo
-- Ingresos y egresos del fondo de reserva (separado del fondo operacional).
CREATE TABLE IF NOT EXISTS movimiento_fondo (
    movimiento_id               SERIAL PRIMARY KEY,
    condominio_id               INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    mantencion_id               INTEGER REFERENCES mantencion(mantencion_id) ON DELETE SET NULL,
    movimiento_tipo             VARCHAR(10) NOT NULL CHECK (movimiento_tipo IN ('INGRESO', 'EGRESO')),
    movimiento_concepto         VARCHAR(300) NOT NULL,
    movimiento_monto            NUMERIC(14, 2) NOT NULL,
    movimiento_fecha            DATE NOT NULL,
    movimiento_saldo_resultante NUMERIC(14, 2) NOT NULL,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mov_fondo_condominio ON movimiento_fondo(condominio_id);

-- Tabla: registro_morosidad
-- Snapshot histórico de morosidad generado al cerrar cada período.
CREATE TABLE IF NOT EXISTS registro_morosidad (
    morosidad_id            SERIAL PRIMARY KEY,
    unidad_id               INTEGER NOT NULL REFERENCES unidad(unidad_id) ON DELETE CASCADE,
    periodo_id              INTEGER NOT NULL REFERENCES periodo_cobro(periodo_id) ON DELETE CASCADE,
    morosidad_meses         INTEGER NOT NULL DEFAULT 1,
    morosidad_monto_total   NUMERIC(14, 2) NOT NULL DEFAULT 0,
    morosidad_activa        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_morosidad_unidad  ON registro_morosidad(unidad_id);
CREATE INDEX IF NOT EXISTS idx_morosidad_periodo ON registro_morosidad(periodo_id);

-- Tabla: corte_suministro
-- Registro probatorio de habilitación para corte de suministro eléctrico.
-- Requiere >= 3 meses de mora y acuerdo de asamblea (Ley 21442).
CREATE TABLE IF NOT EXISTS corte_suministro (
    corte_id                    SERIAL PRIMARY KEY,
    unidad_id                   INTEGER NOT NULL REFERENCES unidad(unidad_id) ON DELETE CASCADE,
    corte_fecha_habilitacion    DATE NOT NULL,
    corte_acuerdo_asamblea      VARCHAR(300),
    corte_meses_mora            INTEGER NOT NULL,
    corte_ejecutado             BOOLEAN NOT NULL DEFAULT FALSE,
    corte_fecha_reposicion      DATE,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_corte_unidad ON corte_suministro(unidad_id);

-- =============================================
-- PERMISOS
-- =============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO citiouser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO citiouser;
