from rest_framework import serializers
from django.db import transaction
from .models import Condominio, Espacio, ActivoTipo, Activo, MantencionEstado, Mantencion, MantencionProgramada


class ActivoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivoTipo
        fields = "__all__"


class MantencionEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantencionEstado
        fields = "__all__"


class MantencionSerializer(serializers.ModelSerializer):
    mantencion_estado_detalle = MantencionEstadoSerializer(source='mantencion_estado', read_only=True)
    activo_nombre = serializers.CharField(source='activo.activo_nombre', read_only=True)

    class Meta:
        model = Mantencion
        fields = [
            'mantencion_id',
            'activo',
            'activo_nombre',
            'mantencion_estado',
            'mantencion_estado_detalle',
            'mantencion_tipo',
            'mantencion_descripcion',
            'mantencion_fecha_realizacion',
            'mantencion_costo',
            'mantencion_realizada_por',
            'created_at',
        ]
        read_only_fields = ['mantencion_id', 'created_at']


class MantencionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantencion
        fields = [
            'activo',
            'mantencion_estado',
            'mantencion_tipo',
            'mantencion_descripcion',
            'mantencion_fecha_realizacion',
            'mantencion_costo',
            'mantencion_realizada_por',
        ]


class MantencionProgramadaSerializer(serializers.ModelSerializer):
    mantencion_estado_detalle = MantencionEstadoSerializer(source='mantencion_estado', read_only=True)
    activo_nombre = serializers.CharField(source='activo.activo_nombre', read_only=True)

    class Meta:
        model = MantencionProgramada
        fields = [
            'mantencion_programada_id',
            'activo',
            'activo_nombre',
            'mantencion_estado',
            'mantencion_estado_detalle',
            'mantencion_programada_descripcion',
            'mantencion_programada_fecha',
            'created_at',
        ]
        read_only_fields = ['mantencion_programada_id', 'created_at']


class MantencionProgramadaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantencionProgramada
        fields = [
            'activo',
            'mantencion_estado',
            'mantencion_programada_descripcion',
            'mantencion_programada_fecha',
        ]


class ActivoSerializer(serializers.ModelSerializer):
    """
    Serializer para activos.
    El condominio es un campo directo requerido.
    El espacio es opcional (puede ser null).
    """
    activo_tipo_detalle = ActivoTipoSerializer(source='activo_tipo', read_only=True)
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.espacio_nombre', read_only=True, allow_null=True)

    class Meta:
        model = Activo
        fields = [
            'activo_id',
            'condominio',
            'condominio_nombre',
            'espacio',
            'espacio_nombre',
            'activo_tipo',
            'activo_tipo_detalle',
            'activo_nombre',
            'activo_marca',
            'activo_modelo',
            'activo_numero_serie',
            'activo_estado',
            'created_at',
        ]
        read_only_fields = ['activo_id', 'created_at', 'condominio_nombre', 'espacio_nombre']


class ActivoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear activos.
    Requiere condominio, espacio es opcional.
    """
    espacio = serializers.PrimaryKeyRelatedField(
        queryset=Espacio.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Activo
        fields = [
            'condominio',
            'espacio',
            'activo_tipo',
            'activo_nombre',
            'activo_marca',
            'activo_modelo',
            'activo_numero_serie',
            'activo_estado',
        ]

    def validate(self, data):
        """
        Valida que si se proporciona un espacio, este pertenezca al condominio indicado.
        """
        espacio = data.get('espacio')
        condominio = data.get('condominio')

        if espacio and espacio.condominio != condominio:
            raise serializers.ValidationError({
                'espacio': 'El espacio debe pertenecer al condominio seleccionado.'
            })

        return data


class EspacioSerializer(serializers.ModelSerializer):
    """
    Serializer para espacios con sus activos.
    """
    activos = ActivoSerializer(many=True, read_only=True)
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)

    class Meta:
        model = Espacio
        fields = [
            'espacio_id',
            'condominio',
            'condominio_nombre',
            'espacio_nombre',
            'espacio_descripcion',
            'ubicacion_fisica',
            'espacio_disponible',
            'activos',
            'created_at',
        ]
        read_only_fields = ['espacio_id', 'created_at']


class EspacioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear espacios.
    """
    class Meta:
        model = Espacio
        fields = [
            'condominio',
            'espacio_nombre',
            'espacio_descripcion',
            'ubicacion_fisica',
            'espacio_disponible',
        ]


class EspacioSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para espacios (sin activos anidados).
    """
    class Meta:
        model = Espacio
        fields = [
            'espacio_id',
            'espacio_nombre',
            'espacio_descripcion',
            'ubicacion_fisica',
            'espacio_disponible',
        ]


class CondominioSerializer(serializers.ModelSerializer):
    """
    Serializer para Condominio con sus espacios y activos.
    """
    espacios = EspacioSerializer(many=True, read_only=True)

    class Meta:
        model = Condominio
        fields = [
            'condominio_id',
            'condominio_nombre',
            'condominio_descripcion',
            'condominio_ubicacion',
            'condominio_activo',
            'espacios',
            'created_at',
        ]
        read_only_fields = ['condominio_id', 'created_at']


class CondominioSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para Condominio (sin espacios anidados).
    """
    class Meta:
        model = Condominio
        fields = [
            'condominio_id',
            'condominio_nombre',
            'condominio_descripcion',
            'condominio_ubicacion',
            'condominio_activo',
            'created_at',
        ]
        read_only_fields = ['condominio_id', 'created_at']


class CondominioConEspaciosCreateSerializer(serializers.Serializer):
    """
    Serializer para crear un condominio junto con sus espacios.
    Formato esperado:
    {
        "condominio_nombre": "...",
        "condominio_descripcion": "...",
        "condominio_ubicacion": "...",
        "espacios": [
            {
                "espacio_nombre": "...",
                "espacio_descripcion": "...",
                "ubicacion_fisica": "..."
            }
        ]
    }
    """
    condominio_nombre = serializers.CharField(max_length=100)
    condominio_descripcion = serializers.CharField(required=False, allow_blank=True)
    condominio_ubicacion = serializers.CharField(required=False, allow_blank=True)
    espacios = EspacioSimpleSerializer(many=True, required=False)

    @transaction.atomic
    def create(self, validated_data):
        espacios_data = validated_data.pop('espacios', [])

        condominio = Condominio.objects.create(**validated_data)

        for espacio_data in espacios_data:
            Espacio.objects.create(condominio=condominio, **espacio_data)

        return condominio
