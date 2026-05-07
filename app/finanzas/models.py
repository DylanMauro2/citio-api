from django.db import models
from django.utils import timezone


ITEM_TIPO_CHOICES = [
    ('ORDINARIO', 'Ordinario'),
    ('EXTRAORDINARIO', 'Extraordinario'),
]

PAGO_MEDIO_CHOICES = [
    ('TRANSFERENCIA', 'Transferencia'),
    ('EFECTIVO', 'Efectivo'),
    ('CHEQUE', 'Cheque'),
    ('OTRO', 'Otro'),
]

MOVIMIENTO_TIPO_CHOICES = [
    ('INGRESO', 'Ingreso'),
    ('EGRESO', 'Egreso'),
]


class Presupuesto(models.Model):
    presupuesto_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        'condominio_gestion.Condominio',
        on_delete=models.CASCADE,
        related_name='presupuestos',
        db_column='condominio_id'
    )
    presupuesto_anio = models.IntegerField()
    presupuesto_monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    presupuesto_aprobado = models.BooleanField(default=False)
    presupuesto_fecha_aprobacion = models.DateField(blank=True, null=True)
    presupuesto_activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'presupuesto'
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-presupuesto_anio']
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'presupuesto_anio'],
                name='uq_presupuesto_condominio_anio'
            )
        ]
        indexes = [
            models.Index(fields=['condominio'], name='idx_presupuesto_condominio'),
        ]

    def __str__(self):
        return f"Presupuesto {self.presupuesto_anio} — {self.condominio.condominio_nombre}"


class ItemPresupuesto(models.Model):
    item_id = models.AutoField(primary_key=True)
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='presupuesto_id'
    )
    item_concepto = models.CharField(max_length=200)
    item_tipo = models.CharField(max_length=20, choices=ITEM_TIPO_CHOICES, default='ORDINARIO')
    item_monto_mensual = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    item_descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'item_presupuesto'
        verbose_name = 'Ítem de Presupuesto'
        verbose_name_plural = 'Ítems de Presupuesto'
        ordering = ['item_tipo', 'item_concepto']
        indexes = [
            models.Index(fields=['presupuesto'], name='idx_item_presupuesto'),
        ]

    def __str__(self):
        return f"{self.item_concepto} ({self.get_item_tipo_display()}) — {self.presupuesto}"


class PeriodoCobro(models.Model):
    periodo_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        'condominio_gestion.Condominio',
        on_delete=models.CASCADE,
        related_name='periodos_cobro',
        db_column='condominio_id'
    )
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.SET_NULL,
        related_name='periodos',
        db_column='presupuesto_id',
        null=True,
        blank=True
    )
    periodo_mes = models.IntegerField()
    periodo_anio = models.IntegerField()
    periodo_fecha_vencimiento = models.DateField()
    periodo_cerrado = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'periodo_cobro'
        verbose_name = 'Período de Cobro'
        verbose_name_plural = 'Períodos de Cobro'
        ordering = ['-periodo_anio', '-periodo_mes']
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'periodo_mes', 'periodo_anio'],
                name='uq_periodo_condominio_mes_anio'
            )
        ]
        indexes = [
            models.Index(fields=['condominio'], name='idx_periodo_condominio'),
        ]

    def __str__(self):
        return f"{self.periodo_mes:02d}/{self.periodo_anio} — {self.condominio.condominio_nombre}"


class CuotaUnidad(models.Model):
    cuota_id = models.AutoField(primary_key=True)
    periodo = models.ForeignKey(
        PeriodoCobro,
        on_delete=models.CASCADE,
        related_name='cuotas',
        db_column='periodo_id'
    )
    unidad = models.ForeignKey(
        'copropietarios.Unidad',
        on_delete=models.CASCADE,
        related_name='cuotas',
        db_column='unidad_id'
    )
    cuota_monto_ordinario = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cuota_monto_extraordinario = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cuota_interes_mora = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cuota_saldo_pendiente = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cuota_pagada = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cuota_unidad'
        verbose_name = 'Cuota por Unidad'
        verbose_name_plural = 'Cuotas por Unidad'
        ordering = ['periodo', 'unidad']
        constraints = [
            models.UniqueConstraint(
                fields=['periodo', 'unidad'],
                name='uq_cuota_periodo_unidad'
            )
        ]
        indexes = [
            models.Index(fields=['periodo'], name='idx_cuota_periodo'),
            models.Index(fields=['unidad'], name='idx_cuota_unidad'),
        ]

    def __str__(self):
        return f"Cuota {self.periodo} — Unidad {self.unidad.unidad_numero}"


class Pago(models.Model):
    pago_id = models.AutoField(primary_key=True)
    cuota = models.ForeignKey(
        CuotaUnidad,
        on_delete=models.CASCADE,
        related_name='pagos',
        db_column='cuota_id'
    )
    pago_fecha = models.DateField()
    pago_monto = models.DecimalField(max_digits=14, decimal_places=2)
    pago_medio = models.CharField(max_length=20, choices=PAGO_MEDIO_CHOICES, default='TRANSFERENCIA')
    pago_referencia = models.CharField(max_length=200, blank=True, null=True)
    pago_registrado_por = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-pago_fecha']
        indexes = [
            models.Index(fields=['cuota'], name='idx_pago_cuota'),
        ]

    def __str__(self):
        return f"Pago ${self.pago_monto} — {self.cuota}"


class MovimientoFondo(models.Model):
    movimiento_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        'condominio_gestion.Condominio',
        on_delete=models.CASCADE,
        related_name='movimientos_fondo',
        db_column='condominio_id'
    )
    mantencion = models.ForeignKey(
        'condominio_gestion.Mantencion',
        on_delete=models.SET_NULL,
        related_name='movimientos_fondo',
        db_column='mantencion_id',
        null=True,
        blank=True
    )
    movimiento_tipo = models.CharField(max_length=10, choices=MOVIMIENTO_TIPO_CHOICES)
    movimiento_concepto = models.CharField(max_length=300)
    movimiento_monto = models.DecimalField(max_digits=14, decimal_places=2)
    movimiento_fecha = models.DateField()
    movimiento_saldo_resultante = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'movimiento_fondo'
        verbose_name = 'Movimiento de Fondo de Reserva'
        verbose_name_plural = 'Movimientos de Fondo de Reserva'
        ordering = ['-movimiento_fecha']
        indexes = [
            models.Index(fields=['condominio'], name='idx_movimiento_fondo_condominio'),
        ]

    def __str__(self):
        return f"{self.get_movimiento_tipo_display()} ${self.movimiento_monto} — {self.movimiento_fecha}"


class RegistroMorosidad(models.Model):
    morosidad_id = models.AutoField(primary_key=True)
    unidad = models.ForeignKey(
        'copropietarios.Unidad',
        on_delete=models.CASCADE,
        related_name='morosidades',
        db_column='unidad_id'
    )
    periodo = models.ForeignKey(
        PeriodoCobro,
        on_delete=models.CASCADE,
        related_name='morosidades',
        db_column='periodo_id'
    )
    morosidad_meses = models.IntegerField(default=1)
    morosidad_monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    morosidad_activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'registro_morosidad'
        verbose_name = 'Registro de Morosidad'
        verbose_name_plural = 'Registros de Morosidad'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['unidad'], name='idx_morosidad_unidad'),
            models.Index(fields=['periodo'], name='idx_morosidad_periodo'),
        ]

    def __str__(self):
        return f"Morosidad Unidad {self.unidad.unidad_numero} — {self.morosidad_meses} mes(es)"


class CorteSuministro(models.Model):
    corte_id = models.AutoField(primary_key=True)
    unidad = models.ForeignKey(
        'copropietarios.Unidad',
        on_delete=models.CASCADE,
        related_name='cortes_suministro',
        db_column='unidad_id'
    )
    corte_fecha_habilitacion = models.DateField()
    corte_acuerdo_asamblea = models.CharField(max_length=300, blank=True, null=True)
    corte_meses_mora = models.IntegerField()
    corte_ejecutado = models.BooleanField(default=False)
    corte_fecha_reposicion = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'corte_suministro'
        verbose_name = 'Corte de Suministro'
        verbose_name_plural = 'Cortes de Suministro'
        ordering = ['-corte_fecha_habilitacion']
        indexes = [
            models.Index(fields=['unidad'], name='idx_corte_unidad'),
        ]

    def __str__(self):
        return f"Corte Unidad {self.unidad.unidad_numero} — {self.corte_fecha_habilitacion}"
