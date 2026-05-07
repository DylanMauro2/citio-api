from django.db import models
from django.utils import timezone


UNIDAD_TIPO_CHOICES = [
    ('DEPARTAMENTO', 'Departamento'),
    ('CASA', 'Casa'),
    ('OFICINA', 'Oficina'),
    ('LOCAL', 'Local Comercial'),
]

TIPO_DOCUMENTO_CHOICES = [
    ('RUT', 'RUT'),
    ('PASAPORTE', 'Pasaporte'),
    ('RNI', 'RNI'),
]

TENENCIA_TIPO_CHOICES = [
    ('PROPIETARIO', 'Propietario'),
    ('ARRENDATARIO', 'Arrendatario'),
    ('OCUPANTE', 'Ocupante'),
]


class Unidad(models.Model):
    """
    Unidad física del condominio (departamento, casa, oficina, local).
    Entidad base a la que se vinculan copropietarios, arrendatarios y ocupantes.
    """
    unidad_id = models.AutoField(primary_key=True)
    condominio = models.ForeignKey(
        'condominio_gestion.Condominio',
        on_delete=models.CASCADE,
        related_name='unidades',
        db_column='condominio_id'
    )
    unidad_numero = models.CharField(max_length=20)
    unidad_piso = models.CharField(max_length=20, blank=True, null=True)
    unidad_block = models.CharField(max_length=20, blank=True, null=True)
    unidad_tipo = models.CharField(
        max_length=20,
        choices=UNIDAD_TIPO_CHOICES,
        default='DEPARTAMENTO'
    )
    unidad_rol_sii = models.CharField(max_length=50, blank=True, null=True)
    unidad_alicuota = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    unidad_superficie_m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unidad_num_estacionamientos = models.IntegerField(default=0)
    unidad_num_bodegas = models.IntegerField(default=0)
    unidad_activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['condominio', 'unidad_block', 'unidad_piso', 'unidad_numero']
        indexes = [
            models.Index(fields=['condominio'], name='idx_unidad_condominio'),
        ]

    def __str__(self):
        partes = [f"Unidad {self.unidad_numero}"]
        if self.unidad_block:
            partes.insert(0, f"Block {self.unidad_block}")
        if self.unidad_piso:
            partes.append(f"Piso {self.unidad_piso}")
        return f"{' - '.join(partes)} ({self.condominio.condominio_nombre})"


class Persona(models.Model):
    """
    Persona natural registrada en el libro de copropietarios.
    Puede ser propietario, arrendatario u ocupante según su RegistroTenencia.
    """
    persona_id = models.AutoField(primary_key=True)
    persona_nombre = models.CharField(max_length=200)
    persona_tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='RUT'
    )
    persona_rut = models.CharField(max_length=20, blank=True, null=True, unique=True)
    persona_email = models.EmailField(blank=True, null=True)
    persona_email_notificaciones = models.EmailField(blank=True, null=True)
    persona_acepta_notificacion_digital = models.BooleanField(default=True)
    persona_telefono = models.CharField(max_length=30, blank=True, null=True)
    persona_domicilio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'persona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['persona_nombre']

    def __str__(self):
        if self.persona_rut:
            return f"{self.persona_nombre} ({self.persona_rut})"
        return self.persona_nombre


class RegistroTenencia(models.Model):
    """
    Vincula una Persona a una Unidad con un rol (propietario, arrendatario, ocupante).
    Mantiene historial completo de cambios de tenencia, cumpliendo el libro de
    registro obligatorio de la Ley N° 21442.
    """
    registro_id = models.AutoField(primary_key=True)
    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.CASCADE,
        related_name='tenencias',
        db_column='unidad_id'
    )
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='tenencias',
        db_column='persona_id'
    )
    tenencia_tipo = models.CharField(max_length=20, choices=TENENCIA_TIPO_CHOICES)
    tenencia_fecha_inicio = models.DateField()
    tenencia_fecha_termino = models.DateField(blank=True, null=True)
    tenencia_activa = models.BooleanField(default=True)
    tenencia_contrato_referencia = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'registro_tenencia'
        verbose_name = 'Registro de Tenencia'
        verbose_name_plural = 'Registros de Tenencia'
        ordering = ['-tenencia_fecha_inicio']
        indexes = [
            models.Index(fields=['unidad'], name='idx_tenencia_unidad'),
            models.Index(fields=['persona'], name='idx_tenencia_persona'),
        ]

    def __str__(self):
        return f"{self.persona.persona_nombre} — {self.get_tenencia_tipo_display()} ({self.unidad})"
