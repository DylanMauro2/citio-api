from rest_framework import viewsets
from .services import generar_cuotas_periodo
from .models import (
    Presupuesto, ItemPresupuesto, PeriodoCobro,
    CuotaUnidad, Pago, MovimientoFondo,
    RegistroMorosidad, CorteSuministro,
)
from .serializer import (
    PresupuestoSerializer, PresupuestoCreateSerializer,
    ItemPresupuestoSerializer, ItemPresupuestoCreateSerializer,
    PeriodoCobroSerializer, PeriodoCobroCreateSerializer,
    CuotaUnidadSerializer, CuotaUnidadCreateSerializer,
    PagoSerializer, PagoCreateSerializer,
    MovimientoFondoSerializer, MovimientoFondoCreateSerializer,
    RegistroMorosidadSerializer, RegistroMorosidadCreateSerializer,
    CorteSuministroSerializer, CorteSuministroCreateSerializer,
)


class PresupuestoView(viewsets.ModelViewSet):
    """
    Presupuestos anuales por condominio.
    Filtros: condominio_id, anio, activo
    """
    queryset = Presupuesto.objects.select_related('condominio').prefetch_related('items').all()
    serializer_class = PresupuestoSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PresupuestoCreateSerializer
        return PresupuestoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(condominio_id=condominio_id)
        if anio := self.request.query_params.get('anio'):
            qs = qs.filter(presupuesto_anio=anio)
        if activo := self.request.query_params.get('activo'):
            qs = qs.filter(presupuesto_activo=activo.lower() == 'true')
        return qs


class ItemPresupuestoView(viewsets.ModelViewSet):
    """
    Ítems de detalle de un presupuesto.
    Filtros: presupuesto_id, tipo
    """
    queryset = ItemPresupuesto.objects.select_related('presupuesto').all()
    serializer_class = ItemPresupuestoSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ItemPresupuestoCreateSerializer
        return ItemPresupuestoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if presupuesto_id := self.request.query_params.get('presupuesto_id'):
            qs = qs.filter(presupuesto_id=presupuesto_id)
        if tipo := self.request.query_params.get('tipo'):
            qs = qs.filter(item_tipo=tipo.upper())
        return qs


class PeriodoCobroView(viewsets.ModelViewSet):
    """
    Períodos mensuales de cobro.
    Filtros: condominio_id, mes, anio, cerrado
    """
    queryset = PeriodoCobro.objects.select_related('condominio', 'presupuesto').all()
    serializer_class = PeriodoCobroSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PeriodoCobroCreateSerializer
        return PeriodoCobroSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(condominio_id=condominio_id)
        if mes := self.request.query_params.get('mes'):
            qs = qs.filter(periodo_mes=mes)
        if anio := self.request.query_params.get('anio'):
            qs = qs.filter(periodo_anio=anio)
        if cerrado := self.request.query_params.get('cerrado'):
            qs = qs.filter(periodo_cerrado=cerrado.lower() == 'true')
        return qs

    def perform_create(self, serializer):
        presupuesto = serializer.validated_data.get('presupuesto')
        if not presupuesto:
            condominio = serializer.validated_data.get('condominio')
            presupuesto = Presupuesto.objects.filter(
                condominio=condominio,
                presupuesto_activo=True,
            ).order_by('-presupuesto_anio').first()

        periodo = serializer.save(presupuesto=presupuesto)
        generar_cuotas_periodo(periodo)


class CuotaUnidadView(viewsets.ModelViewSet):
    """
    Cuotas prorrateadas por unidad para cada período.
    Filtros: periodo_id, unidad_id, condominio_id, pagada
    """
    queryset = CuotaUnidad.objects.select_related(
        'periodo', 'periodo__condominio', 'unidad'
    ).prefetch_related('pagos').all()
    serializer_class = CuotaUnidadSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CuotaUnidadCreateSerializer
        return CuotaUnidadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if periodo_id := self.request.query_params.get('periodo_id'):
            qs = qs.filter(periodo_id=periodo_id)
        if unidad_id := self.request.query_params.get('unidad_id'):
            qs = qs.filter(unidad_id=unidad_id)
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(periodo__condominio_id=condominio_id)
        if pagada := self.request.query_params.get('pagada'):
            qs = qs.filter(cuota_pagada=pagada.lower() == 'true')
        return qs


class PagoView(viewsets.ModelViewSet):
    """
    Pagos registrados por cuota.
    Filtros: cuota_id, unidad_id, medio
    """
    queryset = Pago.objects.select_related('cuota', 'cuota__unidad', 'cuota__periodo').all()
    serializer_class = PagoSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PagoCreateSerializer
        return PagoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if cuota_id := self.request.query_params.get('cuota_id'):
            qs = qs.filter(cuota_id=cuota_id)
        if unidad_id := self.request.query_params.get('unidad_id'):
            qs = qs.filter(cuota__unidad_id=unidad_id)
        if medio := self.request.query_params.get('medio'):
            qs = qs.filter(pago_medio=medio.upper())
        return qs


class MovimientoFondoView(viewsets.ModelViewSet):
    """
    Movimientos del fondo de reserva.
    Filtros: condominio_id, tipo
    """
    queryset = MovimientoFondo.objects.select_related('condominio', 'mantencion').all()
    serializer_class = MovimientoFondoSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MovimientoFondoCreateSerializer
        return MovimientoFondoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(condominio_id=condominio_id)
        if tipo := self.request.query_params.get('tipo'):
            qs = qs.filter(movimiento_tipo=tipo.upper())
        return qs


class RegistroMorosidadView(viewsets.ModelViewSet):
    """
    Registros de morosidad por unidad.
    Filtros: unidad_id, periodo_id, condominio_id, activa
    """
    queryset = RegistroMorosidad.objects.select_related(
        'unidad', 'unidad__condominio', 'periodo'
    ).all()
    serializer_class = RegistroMorosidadSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RegistroMorosidadCreateSerializer
        return RegistroMorosidadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if unidad_id := self.request.query_params.get('unidad_id'):
            qs = qs.filter(unidad_id=unidad_id)
        if periodo_id := self.request.query_params.get('periodo_id'):
            qs = qs.filter(periodo_id=periodo_id)
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(unidad__condominio_id=condominio_id)
        if activa := self.request.query_params.get('activa'):
            qs = qs.filter(morosidad_activa=activa.lower() == 'true')
        return qs


class CorteSuministroView(viewsets.ModelViewSet):
    """
    Registros de corte de suministro eléctrico.
    Filtros: unidad_id, condominio_id, ejecutado
    """
    queryset = CorteSuministro.objects.select_related('unidad', 'unidad__condominio').all()
    serializer_class = CorteSuministroSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CorteSuministroCreateSerializer
        return CorteSuministroSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if unidad_id := self.request.query_params.get('unidad_id'):
            qs = qs.filter(unidad_id=unidad_id)
        if condominio_id := self.request.query_params.get('condominio_id'):
            qs = qs.filter(unidad__condominio_id=condominio_id)
        if ejecutado := self.request.query_params.get('ejecutado'):
            qs = qs.filter(corte_ejecutado=ejecutado.lower() == 'true')
        return qs
