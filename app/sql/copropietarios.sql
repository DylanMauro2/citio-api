-- =============================================
-- SCRIPT DE COPROPIETARIOS
-- Ley N° 21442 — Libro de Registro Obligatorio
-- =============================================

-- =============================================
-- DROP TABLES (orden inverso a dependencias)
-- =============================================
DROP TABLE IF EXISTS registro_tenencia CASCADE;
DROP TABLE IF EXISTS unidad CASCADE;
DROP TABLE IF EXISTS persona CASCADE;

-- Tabla: persona
-- Persona natural: copropietario, arrendatario u ocupante.
CREATE TABLE IF NOT EXISTS persona (
    persona_id      SERIAL PRIMARY KEY,
    persona_nombre  VARCHAR(200) NOT NULL,
    persona_rut     VARCHAR(20)  UNIQUE,
    persona_email   VARCHAR(254),
    persona_telefono VARCHAR(30),
    persona_domicilio TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: unidad
-- Unidad física del condominio (departamento, casa, oficina, local).
CREATE TABLE IF NOT EXISTS unidad (
    unidad_id       SERIAL PRIMARY KEY,
    condominio_id   INTEGER NOT NULL REFERENCES condominio(condominio_id) ON DELETE CASCADE,
    unidad_numero   VARCHAR(20) NOT NULL,
    unidad_piso     VARCHAR(20),
    unidad_block    VARCHAR(20),
    unidad_tipo     VARCHAR(20) NOT NULL DEFAULT 'DEPARTAMENTO'
                        CHECK (unidad_tipo IN ('DEPARTAMENTO', 'CASA', 'OFICINA', 'LOCAL')),
    unidad_rol_sii  VARCHAR(50),
    unidad_activa   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_unidad_condominio ON unidad(condominio_id);

-- Tabla: registro_tenencia
-- Vincula una persona a una unidad con un rol específico.
-- Permite historial completo de cambios de tenencia.
CREATE TABLE IF NOT EXISTS registro_tenencia (
    registro_id             SERIAL PRIMARY KEY,
    unidad_id               INTEGER NOT NULL REFERENCES unidad(unidad_id) ON DELETE CASCADE,
    persona_id              INTEGER NOT NULL REFERENCES persona(persona_id) ON DELETE CASCADE,
    tenencia_tipo           VARCHAR(20) NOT NULL
                                CHECK (tenencia_tipo IN ('PROPIETARIO', 'ARRENDATARIO', 'OCUPANTE')),
    tenencia_fecha_inicio   DATE NOT NULL,
    tenencia_fecha_termino  DATE,
    tenencia_activa         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tenencia_unidad  ON registro_tenencia(unidad_id);
CREATE INDEX IF NOT EXISTS idx_tenencia_persona ON registro_tenencia(persona_id);

-- =============================================
-- PERMISOS
-- =============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO citiouser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO citiouser;

-- =============================================
-- ALTERACIONES — 2026-05-07
-- Nuevos campos requeridos por Módulo 4 (Finanzas)
-- y mejoras de calidad del módulo de copropietarios.
-- =============================================

-- persona: tipo de documento (permite extranjeros con pasaporte/RNI)
ALTER TABLE persona
    ADD COLUMN IF NOT EXISTS persona_tipo_documento VARCHAR(20) NOT NULL DEFAULT 'RUT'
        CHECK (persona_tipo_documento IN ('RUT', 'PASAPORTE', 'RNI'));

-- persona: correo oficial para notificaciones legales (Art. 36 Ley 21442)
ALTER TABLE persona
    ADD COLUMN IF NOT EXISTS persona_email_notificaciones VARCHAR(254);

-- persona: constancia de aceptación de notificación digital (Art. 36 Ley 21442)
ALTER TABLE persona
    ADD COLUMN IF NOT EXISTS persona_acepta_notificacion_digital BOOLEAN NOT NULL DEFAULT TRUE;

-- unidad: alícuota de participación en gastos comunes (crítico para prorrateo — Módulo 4)
ALTER TABLE unidad
    ADD COLUMN IF NOT EXISTS unidad_alicuota NUMERIC(7, 4);

-- unidad: superficie en m² (base alternativa de prorrateo)
ALTER TABLE unidad
    ADD COLUMN IF NOT EXISTS unidad_superficie_m2 NUMERIC(10, 2);

-- unidad: número de estacionamientos asignados
ALTER TABLE unidad
    ADD COLUMN IF NOT EXISTS unidad_num_estacionamientos INTEGER NOT NULL DEFAULT 0;

-- unidad: número de bodegas asignadas
ALTER TABLE unidad
    ADD COLUMN IF NOT EXISTS unidad_num_bodegas INTEGER NOT NULL DEFAULT 0;

-- registro_tenencia: referencia al contrato (para arrendatarios)
ALTER TABLE registro_tenencia
    ADD COLUMN IF NOT EXISTS tenencia_contrato_referencia VARCHAR(200);
