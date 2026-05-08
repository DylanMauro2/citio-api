from decimal import Decimal
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from condominio_gestion.models import Condominio
from core.excel.views import ImportarExcelView
from .excel.mapeos import MAPEO_UNIDADES
from .models import Unidad, Persona, RegistroTenencia
from .serializer import (
    UnidadSerializer,
    UnidadCreateSerializer,
    UnidadConTenenciaCreateSerializer,
    PersonaSerializer,
    PersonaCreateSerializer,
    RegistroTenenciaSerializer,
    RegistroTenenciaCreateSerializer,
)


class UnidadView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar unidades del condominio.
    Filtros disponibles: condominio_id, unidad_tipo, activa
    """
    queryset = Unidad.objects.select_related('condominio').prefetch_related('tenencias__persona').all()
    serializer_class = UnidadSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UnidadConTenenciaCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UnidadCreateSerializer
        return UnidadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        condominio_id = self.request.query_params.get('condominio_id')
        unidad_tipo = self.request.query_params.get('unidad_tipo')
        activa = self.request.query_params.get('activa')

        if condominio_id:
            queryset = queryset.filter(condominio_id=condominio_id)
        if unidad_tipo:
            queryset = queryset.filter(unidad_tipo=unidad_tipo)
        if activa is not None:
            queryset = queryset.filter(unidad_activa=activa.lower() == 'true')

        return queryset


class PersonaView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar personas (copropietarios, arrendatarios, ocupantes).
    Filtros disponibles: unidad_id, tenencia_tipo
    """
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PersonaCreateSerializer
        return PersonaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        unidad_id = self.request.query_params.get('unidad_id')
        tenencia_tipo = self.request.query_params.get('tenencia_tipo')

        if unidad_id:
            queryset = queryset.filter(
                tenencias__unidad_id=unidad_id,
                tenencias__tenencia_activa=True
            )
        if tenencia_tipo:
            queryset = queryset.filter(
                tenencias__tenencia_tipo=tenencia_tipo,
                tenencias__tenencia_activa=True
            )

        return queryset.distinct()


class RegistroTenenciaView(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el historial de tenencias por unidad.
    Filtros disponibles: unidad_id, persona_id, tenencia_tipo, activa, condominio_id
    """
    queryset = RegistroTenencia.objects.select_related(
        'unidad',
        'unidad__condominio',
        'persona'
    ).all()
    serializer_class = RegistroTenenciaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RegistroTenenciaCreateSerializer
        return RegistroTenenciaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        unidad_id = self.request.query_params.get('unidad_id')
        persona_id = self.request.query_params.get('persona_id')
        tenencia_tipo = self.request.query_params.get('tenencia_tipo')
        activa = self.request.query_params.get('activa')
        condominio_id = self.request.query_params.get('condominio_id')

        if unidad_id:
            queryset = queryset.filter(unidad_id=unidad_id)
        if persona_id:
            queryset = queryset.filter(persona_id=persona_id)
        if tenencia_tipo:
            queryset = queryset.filter(tenencia_tipo=tenencia_tipo)
        if activa is not None:
            queryset = queryset.filter(tenencia_activa=activa.lower() == 'true')
        if condominio_id:
            queryset = queryset.filter(unidad__condominio_id=condominio_id)

        return queryset


TIPOS_UNIDAD_VALIDOS = {'DEPARTAMENTO', 'CASA', 'OFICINA', 'LOCAL'}

_respuesta_importar = openapi.Response(
    description='Resultado del procesamiento del Excel',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'total_filas':   openapi.Schema(type=openapi.TYPE_INTEGER),
            'total_errores': openapi.Schema(type=openapi.TYPE_INTEGER),
            'valido':        openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'data':          openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
            'errores':       openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
)


class ImportarUnidadesView(ImportarExcelView):
    mapeo = MAPEO_UNIDADES

    @swagger_auto_schema(
        operation_summary='Importar unidades desde Excel',
        operation_description=(
            'Procesa un archivo .xlsx con unidades del condominio. '
            'Columnas esperadas: A=condominio_id, B=numero, C=tipo, '
            'D=piso, E=block, F=rol_sii, G=alicuota, H=superficie_m2'
        ),
        manual_parameters=[
            openapi.Parameter(
                name='archivo',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Archivo Excel (.xlsx)',
            )
        ],
        responses={200: _respuesta_importar},
    )
    def post(self, request):
        return super().post(request)

    def validar(self, data: list, errores: list) -> None:
        condominios_existentes = set(
            Condominio.objects.values_list('condominio_id', flat=True)
        )

        for fila in data:
            self._validar_condominio(fila, errores, condominios_existentes)
            self._validar_tipo(fila, errores)
            self._validar_alicuota(fila, errores)
            self._validar_superficie(fila, errores)

    def _validar_condominio(self, fila, errores, condominios_existentes):
        campo = fila.get('condominio_id', {})
        if campo.get('error') or campo.get('valor') is None:
            return
        if campo['valor'] not in condominios_existentes:
            campo['error'] = True
            errores.append({
                'celda': campo['celda'],
                'campo': 'condominio_id',
                'valor': campo['valor'],
                'descripcion': f"No existe ningún condominio con ID {campo['valor']}.",
            })

    def _validar_tipo(self, fila, errores):
        campo = fila.get('tipo', {})
        if campo.get('error') or campo.get('valor') is None:
            return
        valor = str(campo['valor']).upper()
        if valor not in TIPOS_UNIDAD_VALIDOS:
            campo['error'] = True
            campo['valor'] = campo['valor']
            errores.append({
                'celda': campo['celda'],
                'campo': 'tipo',
                'valor': campo['valor'],
                'descripcion': f"Tipo de unidad inválido. Valores permitidos: {', '.join(sorted(TIPOS_UNIDAD_VALIDOS))}.",
            })

    def _validar_alicuota(self, fila, errores):
        campo = fila.get('alicuota', {})
        if campo.get('error') or campo.get('valor') is None:
            return
        try:
            valor = Decimal(str(campo['valor']))
            if not (Decimal('0') < valor <= Decimal('100')):
                raise ValueError()
        except Exception:
            campo['error'] = True
            errores.append({
                'celda': campo['celda'],
                'campo': 'alicuota',
                'valor': campo['valor'],
                'descripcion': "La alícuota debe ser un número mayor a 0 y máximo 100.",
            })

    def _validar_superficie(self, fila, errores):
        campo = fila.get('superficie_m2', {})
        if campo.get('error') or campo.get('valor') is None:
            return
        try:
            if Decimal(str(campo['valor'])) <= Decimal('0'):
                raise ValueError()
        except Exception:
            campo['error'] = True
            errores.append({
                'celda': campo['celda'],
                'campo': 'superficie_m2',
                'valor': campo['valor'],
                'descripcion': "La superficie debe ser un número mayor a 0.",
            })
