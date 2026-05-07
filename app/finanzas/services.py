from decimal import Decimal
from django.db.models import Sum
from copropietarios.models import Unidad
from .models import CuotaUnidad, PeriodoCobro


def generar_cuotas_periodo(periodo: PeriodoCobro) -> int:
    """
    Genera una CuotaUnidad por cada Unidad activa del condominio.
    Llamado automáticamente al crear un PeriodoCobro.
    Retorna la cantidad de cuotas generadas.
    """
    unidades = Unidad.objects.filter(
        condominio=periodo.condominio,
        unidad_activa=True,
    )

    total_mensual = Decimal('0')
    if periodo.presupuesto_id:
        total_mensual = periodo.presupuesto.items.filter(
            item_tipo='ORDINARIO'
        ).aggregate(total=Sum('item_monto_mensual'))['total'] or Decimal('0')

    cuotas = []
    for unidad in unidades:
        if unidad.unidad_alicuota:
            monto_ordinario = (total_mensual * unidad.unidad_alicuota / Decimal('100')).quantize(Decimal('0.01'))
        else:
            monto_ordinario = Decimal('0')

        interes_mora = _calcular_interes_mora(unidad, periodo)
        saldo = monto_ordinario + interes_mora

        cuotas.append(CuotaUnidad(
            periodo=periodo,
            unidad=unidad,
            cuota_monto_ordinario=monto_ordinario,
            cuota_monto_extraordinario=Decimal('0'),
            cuota_interes_mora=interes_mora,
            cuota_saldo_pendiente=saldo,
            cuota_pagada=False,
        ))

    CuotaUnidad.objects.bulk_create(cuotas)
    return len(cuotas)


def _calcular_interes_mora(unidad: Unidad, periodo: PeriodoCobro) -> Decimal:
    """
    Suma los saldos pendientes de cuotas anteriores sin pagar para esta unidad.
    El interés sobre esos saldos se aplica al crear el nuevo período.
    Tasa: 0.1% mensual (referencial; ajustar según interés máximo convencional vigente).
    """
    TASA_MENSUAL = Decimal('0.001')

    saldo_moroso = CuotaUnidad.objects.filter(
        unidad=unidad,
        cuota_pagada=False,
        periodo__condominio=periodo.condominio,
        periodo__periodo_anio__lte=periodo.periodo_anio,
    ).exclude(
        periodo=periodo
    ).aggregate(total=Sum('cuota_saldo_pendiente'))['total'] or Decimal('0')

    return (saldo_moroso * TASA_MENSUAL).quantize(Decimal('0.01'))
