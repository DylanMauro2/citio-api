from rest_framework import serializers
from django.db import transaction
from .models import Condominio, Espacio, ActivoTipo, Activo, MantencionProveedor, MantencionEstado, Mantencion, MantencionProgramada, MANTENCION_TIPO_CHOICES


class ActivoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivoTipo
        fields = "__all__"


class MantencionProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantencionProveedor
        fields = "__all__"
        read_only_fields = ['mantencion_proveedor_id', 'created_at', 'updated_at']


class MantencionProveedorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantencionProveedor
        fields = [
            'mantencion_proveedor_nombre',
            'mantencion_proveedor_rut',
            'mantencion_proveedor_activo',
            'mantencion_proveedor_telefono',
            'mantencion_proveedor_email',
            'mantencion_proveedor_administrador',
        ]


class MantencionEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantencionEstado
        fields = "__all__"


class MantencionSerializer(serializers.ModelSerializer):
    mantencion_estado_detalle = MantencionEstadoSerializer(source='mantencion_estado', read_only=True)
    mantencion_proveedor_detalle = MantencionProveedorSerializer(source='mantencion_proveedor', read_only=True)
    activo_nombre = serializers.CharField(source='activo.activo_nombre', read_only=True)

    class Meta:
        model = Mantencion
        fields = [
            'mantencion_id',
            'activo',
            'activo_nombre',
            'mantencion_proveedor',
            'mantencion_proveedor_detalle',
            'mantencion_estado',
            'mantencion_estado_detalle',
            'mantencion_tipo',
            'mantencion_descripcion',
            'mantencion_fecha_realizacion',
            'mantencion_hora',
            'mantencion_tecnico_nombre',
            'mantencion_tecnico_rut',
            'mantencion_tecnico_telefono',
            'mantencion_tecnico_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['mantencion_id', 'created_at', 'updated_at']


class MantencionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantencion
        fields = [
            'activo',
            'mantencion_proveedor',
            'mantencion_estado',
            'mantencion_tipo',
            'mantencion_descripcion',
            'mantencion_fecha_realizacion',
            'mantencion_hora',
            'mantencion_tecnico_nombre',
            'mantencion_tecnico_rut',
            'mantencion_tecnico_telefono',
            'mantencion_tecnico_email',
        ]


class MantencionProgramadaSerializer(serializers.ModelSerializer):
    mantencion_detalle = MantencionSerializer(source='mantencion', read_only=True)

    class Meta:
        model = MantencionProgramada
        fields = [
            'mantencion_programada_id',
            'mantencion',
            'mantencion_detalle',
            'mantencion_programada_fecha',
            'mantencion_programada_descripcion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['mantencion_programada_id', 'created_at', 'updated_at']


class MantencionProgramadaCreateSerializer(serializers.Serializer):
    """
    Crea una MantencionProgramada junto con su Mantencion en una sola operación.

    Primero crea la Mantencion con los campos básicos (activo, proveedor, estado, tipo, descripcion).
    Luego crea la MantencionProgramada con la fecha y descripción del calendario.

    Campos requeridos:
    - activo
    - mantencion_programada_fecha

    Campos opcionales de la Mantencion:
    - mantencion_proveedor
    - mantencion_estado (por defecto: PENDIENTE)
    - mantencion_tipo
    - mantencion_descripcion (describe el trabajo realizado)

    Campos opcionales de la MantencionProgramada:
    - mantencion_programada_descripcion (descripción visible en el calendario)
    """
    # Campos de Mantencion
    activo = serializers.PrimaryKeyRelatedField(queryset=Activo.objects.all())
    mantencion_proveedor = serializers.PrimaryKeyRelatedField(
        queryset=MantencionProveedor.objects.all(),
        required=False,
        allow_null=True
    )
    mantencion_estado = serializers.PrimaryKeyRelatedField(
        queryset=MantencionEstado.objects.all(),
        required=False,
        allow_null=True
    )
    mantencion_tipo = serializers.ChoiceField(
        choices=MANTENCION_TIPO_CHOICES,
        required=False,
        allow_null=True
    )
    mantencion_descripcion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    # Campos de MantencionProgramada
    mantencion_programada_fecha = serializers.DateField()
    mantencion_programada_descripcion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def to_representation(self, instance):
        return MantencionProgramadaSerializer(instance).data

    @transaction.atomic
    def create(self, validated_data):
        # Extraer campos propios de MantencionProgramada
        mantencion_programada_fecha = validated_data.pop('mantencion_programada_fecha')
        mantencion_programada_descripcion = validated_data.pop('mantencion_programada_descripcion', None)

        # Usar estado enviado o por defecto PENDIENTE
        if 'mantencion_estado' not in validated_data or validated_data.get('mantencion_estado') is None:
            validated_data['mantencion_estado'] = MantencionEstado.objects.get(pk='PENDIENTE')

        # Crear Mantencion solo con los campos básicos
        mantencion = Mantencion.objects.create(**validated_data)

        mantencion_programada = MantencionProgramada.objects.create(
            mantencion=mantencion,
            mantencion_programada_fecha=mantencion_programada_fecha,
            mantencion_programada_descripcion=mantencion_programada_descripcion,
        )

        return mantencion_programada


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
