from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import (
    ActivoTipoSerializer,
    ActivoSerializer,
    ActivoCreateSerializer,
    EspacioSerializer,
    EspacioCreateSerializer,
    CondominioSerializer,
    CondominioSimpleSerializer,
    CondominioConEspaciosCreateSerializer,
    MantencionEstadoSerializer,
    MantencionSerializer,
    MantencionCreateSerializer,
    MantencionProgramadaSerializer,
    MantencionProgramadaCreateSerializer,
)
from .models import ActivoTipo, Activo, Espacio, Condominio, MantencionEstado, Mantencion, MantencionProgramada


class ActivoTipoView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de activos (catálogo).
    """
    queryset = ActivoTipo.objects.all()
    serializer_class = ActivoTipoSerializer


class ActivoView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar activos.
    Los activos pertenecen directamente a un condominio.
    Opcionalmente pueden estar asociados a un espacio específico.
    """
    queryset = Activo.objects.select_related('condominio', 'espacio', 'activo_tipo').all()
    serializer_class = ActivoSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ActivoCreateSerializer
        return ActivoSerializer

    def get_queryset(self):
        """
        Opcionalmente filtra activos por condominio o espacio.
        Ejemplo: /activo/?condominio_id=1&espacio_id=2
        """
        queryset = super().get_queryset()
        condominio_id = self.request.query_params.get('condominio_id')
        espacio_id = self.request.query_params.get('espacio_id')

        if condominio_id:
            queryset = queryset.filter(condominio_id=condominio_id)
        if espacio_id:
            queryset = queryset.filter(espacio_id=espacio_id)

        return queryset


class EspacioView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar espacios.
    Los espacios pertenecen a condominios y contienen activos.
    """
    queryset = Espacio.objects.select_related('condominio').prefetch_related('activos').all()
    serializer_class = EspacioSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EspacioCreateSerializer
        return EspacioSerializer

    def get_queryset(self):
        """
        Opcionalmente filtra espacios por condominio.
        Ejemplo: /espacio/?condominio_id=1
        """
        queryset = super().get_queryset()
        condominio_id = self.request.query_params.get('condominio_id')

        if condominio_id:
            queryset = queryset.filter(condominio_id=condominio_id)

        return queryset


class CondominioView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar condominios.
    El condominio actúa como "sucursal" o contexto principal.
    """
    queryset = Condominio.objects.prefetch_related('espacios', 'activos').all()
    serializer_class = CondominioSerializer

    def get_serializer_class(self):
        if self.action == 'crear_con_espacios':
            return CondominioConEspaciosCreateSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CondominioSimpleSerializer
        return CondominioSerializer

    @swagger_auto_schema(
        method='post',
        request_body=CondominioConEspaciosCreateSerializer,
        responses={
            201: openapi.Response(
                description="Condominio creado exitosamente con sus espacios",
                schema=CondominioSerializer
            ),
            400: openapi.Response(description="Error de validación")
        },
        operation_description="""
        Crear un condominio junto con sus espacios.

        Formato del body:
        {
            "condominio_nombre": "Nombre del condominio",
            "condominio_descripcion": "Descripción opcional",
            "condominio_ubicacion": "Ubicación del condominio",
            "espacios": [
                {
                    "espacio_nombre": "Hall de entrada",
                    "espacio_descripcion": "Área común de entrada",
                    "ubicacion_fisica": "Piso 1"
                }
            ]
        }

        Notas:
        - El campo "espacios" es opcional. Puedes crear un condominio sin espacios.
        - Los activos se agregan posteriormente a los espacios.
        """
    )
    @action(detail=False, methods=['post'], url_path='crear-con-espacios')
    def crear_con_espacios(self, request):
        """
        Endpoint para crear un condominio con sus espacios.
        URL: POST /condominio/crear-con-espacios/
        """
        serializer = CondominioConEspaciosCreateSerializer(data=request.data)

        if serializer.is_valid():
            condominio = serializer.save()
            condominio_serializer = CondominioSerializer(condominio)

            return Response(
                {
                    'message': 'Condominio creado exitosamente',
                    'data': condominio_serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MantencionEstadoView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el catálogo de estados de mantención.
    """
    queryset = MantencionEstado.objects.all()
    serializer_class = MantencionEstadoSerializer


class MantencionView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mantenciones realizadas.
    Filtros disponibles: activo_id, condominio_id, mantencion_estado_code
    """
    queryset = Mantencion.objects.select_related(
        'activo', 'activo__condominio', 'mantencion_estado'
    ).all()
    serializer_class = MantencionSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MantencionCreateSerializer
        return MantencionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        activo_id = self.request.query_params.get('activo_id')
        condominio_id = self.request.query_params.get('condominio_id')
        mantencion_estado_code = self.request.query_params.get('mantencion_estado_code')

        if activo_id:
            queryset = queryset.filter(activo_id=activo_id)
        if condominio_id:
            queryset = queryset.filter(activo__condominio_id=condominio_id)
        if mantencion_estado_code:
            queryset = queryset.filter(mantencion_estado_code=mantencion_estado_code)

        return queryset


class MantencionProgramadaView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mantenciones programadas.
    Filtros disponibles: activo_id, condominio_id, mantencion_estado_code
    """
    queryset = MantencionProgramada.objects.select_related(
        'activo', 'activo__condominio', 'mantencion_estado'
    ).all()
    serializer_class = MantencionProgramadaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MantencionProgramadaCreateSerializer
        return MantencionProgramadaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        activo_id = self.request.query_params.get('activo_id')
        condominio_id = self.request.query_params.get('condominio_id')
        mantencion_estado_code = self.request.query_params.get('mantencion_estado_code')

        if activo_id:
            queryset = queryset.filter(activo_id=activo_id)
        if condominio_id:
            queryset = queryset.filter(activo__condominio_id=condominio_id)
        if mantencion_estado_code:
            queryset = queryset.filter(mantencion_estado_code=mantencion_estado_code)

        return queryset
