from rest_framework import viewsets
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
