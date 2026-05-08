from rest_framework import serializers
from django.db import transaction
from .models import Unidad, Persona, RegistroTenencia


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'
        read_only_fields = ['persona_id', 'created_at', 'updated_at']


class PersonaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = [
            'persona_nombre',
            'persona_rut',
            'persona_email',
            'persona_telefono',
            'persona_domicilio',
        ]


class TenenciaActivaSerializer(serializers.ModelSerializer):
    """Serializer liviano para mostrar tenencias activas anidadas en una Unidad."""
    persona_detalle = PersonaSerializer(source='persona', read_only=True)
    tenencia_tipo_display = serializers.CharField(source='get_tenencia_tipo_display', read_only=True)

    class Meta:
        model = RegistroTenencia
        fields = [
            'registro_id',
            'persona',
            'persona_detalle',
            'tenencia_tipo',
            'tenencia_tipo_display',
            'tenencia_fecha_inicio',
        ]


class UnidadSerializer(serializers.ModelSerializer):
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)
    tenencias_activas = serializers.SerializerMethodField()

    def get_tenencias_activas(self, obj):
        tenencias = obj.tenencias.filter(tenencia_activa=True).select_related('persona')
        return TenenciaActivaSerializer(tenencias, many=True).data

    class Meta:
        model = Unidad
        fields = [
            'unidad_id',
            'condominio',
            'condominio_nombre',
            'unidad_numero',
            'unidad_piso',
            'unidad_block',
            'unidad_tipo',
            'unidad_rol_sii',
            'unidad_alicuota',
            'unidad_superficie_m2',
            'unidad_num_estacionamientos',
            'unidad_num_bodegas',
            'unidad_activa',
            'tenencias_activas',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['unidad_id', 'created_at', 'updated_at']


class UnidadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = [
            'condominio',
            'unidad_numero',
            'unidad_piso',
            'unidad_block',
            'unidad_tipo',
            'unidad_rol_sii',
            'unidad_alicuota',
            'unidad_superficie_m2',
            'unidad_num_estacionamientos',
            'unidad_num_bodegas',
            'unidad_activa',
        ]


class TenenciaInlineSerializer(serializers.Serializer):
    """Serializer para el registro de tenencia opcional al crear una unidad."""
    persona = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())
    tenencia_tipo = serializers.ChoiceField(choices=[
        ('PROPIETARIO', 'Propietario'),
        ('ARRENDATARIO', 'Arrendatario'),
        ('OCUPANTE', 'Ocupante'),
    ])
    tenencia_fecha_inicio = serializers.DateField()
    tenencia_fecha_termino = serializers.DateField(required=False, allow_null=True)


class UnidadConTenenciaCreateSerializer(serializers.Serializer):
    """
    Crea una Unidad y opcionalmente su RegistroTenencia inicial en una sola operación.

    Body mínimo:
    {
        "condominio": 1,
        "unidad_numero": "302",
        "unidad_tipo": "DEPARTAMENTO"
    }

    Body con tenencia:
    {
        "condominio": 1,
        "unidad_numero": "302",
        "unidad_tipo": "DEPARTAMENTO",
        "registro_tenencia": {
            "persona": 5,
            "tenencia_tipo": "PROPIETARIO",
            "tenencia_fecha_inicio": "2026-01-01"
        }
    }
    """
    condominio = serializers.PrimaryKeyRelatedField(
        queryset=Unidad._meta.get_field('condominio').related_model.objects.all()
    )
    unidad_numero = serializers.CharField(max_length=20)
    unidad_piso = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    unidad_block = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    unidad_tipo = serializers.ChoiceField(choices=[
        ('DEPARTAMENTO', 'Departamento'),
        ('CASA', 'Casa'),
        ('OFICINA', 'Oficina'),
        ('LOCAL', 'Local Comercial'),
    ], default='DEPARTAMENTO')
    unidad_rol_sii = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    unidad_alicuota = serializers.DecimalField(max_digits=7, decimal_places=4, required=False, allow_null=True)
    unidad_superficie_m2 = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    unidad_num_estacionamientos = serializers.IntegerField(default=0, required=False)
    unidad_num_bodegas = serializers.IntegerField(default=0, required=False)
    unidad_activa = serializers.BooleanField(default=True)
    registro_tenencia = TenenciaInlineSerializer(required=False, allow_null=True)

    def to_representation(self, instance):
        return UnidadSerializer(instance).data

    @transaction.atomic
    def create(self, validated_data):
        tenencia_data = validated_data.pop('registro_tenencia', None)

        unidad = Unidad.objects.create(**validated_data)

        if tenencia_data:
            RegistroTenencia.objects.create(unidad=unidad, **tenencia_data)

        return unidad


class RegistroTenenciaSerializer(serializers.ModelSerializer):
    persona_detalle = PersonaSerializer(source='persona', read_only=True)
    tenencia_tipo_display = serializers.CharField(source='get_tenencia_tipo_display', read_only=True)
    unidad_numero = serializers.CharField(source='unidad.unidad_numero', read_only=True)
    condominio_nombre = serializers.CharField(source='unidad.condominio.condominio_nombre', read_only=True)

    class Meta:
        model = RegistroTenencia
        fields = [
            'registro_id',
            'unidad',
            'unidad_numero',
            'condominio_nombre',
            'persona',
            'persona_detalle',
            'tenencia_tipo',
            'tenencia_tipo_display',
            'tenencia_fecha_inicio',
            'tenencia_fecha_termino',
            'tenencia_activa',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['registro_id', 'created_at', 'updated_at']


class RegistroTenenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTenencia
        fields = [
            'unidad',
            'persona',
            'tenencia_tipo',
            'tenencia_fecha_inicio',
            'tenencia_fecha_termino',
            'tenencia_activa',
        ]
