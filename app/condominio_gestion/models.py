from django.db import models
from django.utils import timezone


ESTADO_ACTIVO_CHOICES = [
    ("ACTIVO", "Activo"),
    ("INACTIVO", "Inactivo"),
    ("EN_MANTENIMIENTO", "En Mantenimiento"),
]

MANTENCION_TIPO_CHOICES = [
    ("PREVENTIVA", "Preventiva"),
    ("CORRECTIVA", "Correctiva"),
    ("EMERGENCIA", "Emergencia"),
]


class Condominio(models.Model):
    """
    Actúa como "sucursal" o contexto principal.
    Todo lo que se agrega dentro de un condominio hereda este contexto.
    """
    condominio_id = models.AutoField(primary_key=True)
    condominio_nombre = models.CharField(max_length=100)
    condominio_descripcion = models.TextField(blank=True, null=True)
    condominio_ubicacion = models.TextField(blank=True, null=True)
    condominio_activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'condominio'
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'
        ordering = ['condominio_nombre']

    def __str__(self):
        return self.condominio_nombre


class Espacio(models.Model):
    """
    Espacio físico dentro de un condominio.
    Los activos se asocian a espacios, heredando el condominio implícitamente.
    """
    espacio_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='espacios',
        db_column='condominio_id'
    )
    espacio_nombre = models.CharField(max_length=100)
    espacio_descripcion = models.TextField(blank=True, null=True)
    ubicacion_fisica = models.TextField(blank=True, null=True)
    espacio_disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'espacio'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['condominio', 'espacio_nombre']
        indexes = [
            models.Index(fields=['condominio'], name='idx_espacio_condominio'),
        ]

    def __str__(self):
        return f"{self.espacio_nombre} - {self.condominio.condominio_nombre}"


class ActivoTipo(models.Model):
    """
    Catálogo de tipos de activos.
    """
    activo_tipo_code = models.CharField(max_length=50, primary_key=True)
    activo_tipo_nombre = models.CharField(max_length=100)
    activo_tipo_descripcion = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'activo_tipo'
        verbose_name = 'Tipo de Activo'
        verbose_name_plural = 'Tipos de Activos'
        ordering = ['activo_tipo_nombre']

    def __str__(self):
        return self.activo_tipo_nombre


class Activo(models.Model):
    """
    Activo físico asociado a un condominio.
    Opcionalmente puede estar asociado a un espacio específico.
    """
    activo_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='activos',
        db_column='condominio_id'
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.SET_NULL,
        related_name='activos',
        db_column='espacio_id',
        null=True,
        blank=True
    )
    activo_tipo = models.ForeignKey(
        ActivoTipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos',
        db_column='activo_tipo_code'
    )
    activo_nombre = models.CharField(max_length=200)
    activo_marca = models.CharField(max_length=100, blank=True, null=True)
    activo_modelo = models.CharField(max_length=100, blank=True, null=True)
    activo_numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    activo_estado = models.CharField(
        max_length=50,
        choices=ESTADO_ACTIVO_CHOICES,
        default="ACTIVO"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'activo'
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        ordering = ['condominio', 'activo_nombre']
        indexes = [
            models.Index(fields=['condominio'], name='idx_activo_condominio'),
            models.Index(fields=['espacio'], name='idx_activo_espacio'),
            models.Index(fields=['activo_tipo'], name='idx_activo_tipo'),
        ]

    def __str__(self):
        if self.espacio:
            return f"{self.activo_nombre} ({self.espacio.espacio_nombre})"
        return f"{self.activo_nombre} ({self.condominio.condominio_nombre})"


class MantencionProveedor(models.Model):
    """
    Proveedor de servicios de mantención.
    """
    mantencion_proveedor_id = models.AutoField(primary_key=True)
    mantencion_proveedor_nombre = models.TextField()
    mantencion_proveedor_rut = models.TextField(blank=True, null=True)
    mantencion_proveedor_activo = models.BooleanField(default=True)
    mantencion_proveedor_telefono = models.TextField(blank=True, null=True)
    mantencion_proveedor_email = models.TextField(blank=True, null=True)
    mantencion_proveedor_administrador = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mantencion_proveedor'
        verbose_name = 'Proveedor de Mantención'
        verbose_name_plural = 'Proveedores de Mantención'
        ordering = ['mantencion_proveedor_nombre']

    def __str__(self):
        return self.mantencion_proveedor_nombre


class MantencionEstado(models.Model):
    """
    Catálogo de estados de mantención.
    """
    mantencion_estado_code = models.CharField(max_length=50, primary_key=True)
    mantencion_estado_nombre = models.CharField(max_length=100)
    mantencion_estado_descripcion = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mantencion_estado'
        verbose_name = 'Estado de Mantención'
        verbose_name_plural = 'Estados de Mantención'
        ordering = ['mantencion_estado_nombre']

    def __str__(self):
        return self.mantencion_estado_nombre


class Mantencion(models.Model):
    """
    Registro completo de una mantención. Puede originarse desde una
    MantencionProgramada o crearse directamente.
    """
    mantencion_id = models.AutoField(primary_key=True)
    activo = models.ForeignKey(
        Activo,
        on_delete=models.CASCADE,
        related_name='mantenciones',
        db_column='activo_id'
    )
    mantencion_proveedor = models.ForeignKey(
        MantencionProveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenciones',
        db_column='mantencion_proveedor_id'
    )
    mantencion_estado = models.ForeignKey(
        MantencionEstado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenciones',
        db_column='mantencion_estado_code'
    )
    mantencion_tipo = models.CharField(
        max_length=50,
        choices=MANTENCION_TIPO_CHOICES,
        blank=True,
        null=True
    )
    mantencion_descripcion = models.TextField(blank=True, null=True)
    mantencion_fecha_realizacion = models.DateField(blank=True, null=True)
    mantencion_hora = models.TextField(blank=True, null=True)
    mantencion_tecnico_nombre = models.TextField(blank=True, null=True)
    mantencion_tecnico_rut = models.TextField(blank=True, null=True)
    mantencion_tecnico_telefono = models.TextField(blank=True, null=True)
    mantencion_tecnico_email = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mantencion'
        verbose_name = 'Mantención'
        verbose_name_plural = 'Mantenciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['activo'], name='idx_mantencion_activo'),
            models.Index(fields=['mantencion_proveedor'], name='idx_mantencion_proveedor'),
        ]

    def __str__(self):
        return f"{self.activo.activo_nombre} - {self.mantencion_estado}"


class MantencionProgramada(models.Model):
    """
    Entrada de calendario para una mantención programada.
    Apunta a la Mantencion que contiene todos los detalles.
    """
    mantencion_programada_id = models.AutoField(primary_key=True)
    mantencion = models.OneToOneField(
        Mantencion,
        on_delete=models.CASCADE,
        related_name='programada',
        db_column='mantencion_id'
    )
    mantencion_programada_fecha = models.DateField()
    mantencion_programada_descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mantencion_programada'
        verbose_name = 'Mantención Programada'
        verbose_name_plural = 'Mantenciones Programadas'
        ordering = ['mantencion_programada_fecha']
        indexes = [
            models.Index(fields=['mantencion'], name='idx_mt_programada_mantencion'),
        ]

    def __str__(self):
        return f"{self.mantencion.activo.activo_nombre} - {self.mantencion_programada_fecha}"
