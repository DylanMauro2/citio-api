from django.contrib import admin
from .models import (
    Presupuesto, ItemPresupuesto, PeriodoCobro,
    CuotaUnidad, Pago, MovimientoFondo,
    RegistroMorosidad, CorteSuministro,
)


class ItemPresupuestoInline(admin.TabularInline):
    model = ItemPresupuesto
    extra = 0
    fields = ['item_concepto', 'item_tipo', 'item_monto_mensual']


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ['presupuesto_id', 'condominio', 'presupuesto_anio', 'presupuesto_monto_total', 'presupuesto_aprobado', 'presupuesto_activo']
    list_filter = ['presupuesto_aprobado', 'presupuesto_activo', 'condominio']
    search_fields = ['condominio__condominio_nombre', 'presupuesto_anio']
    ordering = ['-presupuesto_anio']
    inlines = [ItemPresupuestoInline]


@admin.register(ItemPresupuesto)
class ItemPresupuestoAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'presupuesto', 'item_concepto', 'item_tipo', 'item_monto_mensual']
    list_filter = ['item_tipo', 'presupuesto__condominio']
    search_fields = ['item_concepto', 'presupuesto__condominio__condominio_nombre']


class CuotaInline(admin.TabularInline):
    model = CuotaUnidad
    extra = 0
    fields = ['unidad', 'cuota_monto_ordinario', 'cuota_monto_extraordinario', 'cuota_saldo_pendiente', 'cuota_pagada']
    readonly_fields = ['cuota_saldo_pendiente']


@admin.register(PeriodoCobro)
class PeriodoCobroAdmin(admin.ModelAdmin):
    list_display = ['periodo_id', 'condominio', 'periodo_mes', 'periodo_anio', 'periodo_fecha_vencimiento', 'periodo_cerrado']
    list_filter = ['periodo_cerrado', 'condominio', 'periodo_anio']
    search_fields = ['condominio__condominio_nombre']
    ordering = ['-periodo_anio', '-periodo_mes']
    inlines = [CuotaInline]


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    fields = ['pago_fecha', 'pago_monto', 'pago_medio', 'pago_referencia']


@admin.register(CuotaUnidad)
class CuotaUnidadAdmin(admin.ModelAdmin):
    list_display = ['cuota_id', 'periodo', 'unidad', 'cuota_monto_ordinario', 'cuota_saldo_pendiente', 'cuota_pagada']
    list_filter = ['cuota_pagada', 'periodo__condominio', 'periodo__periodo_anio']
    search_fields = ['unidad__unidad_numero', 'periodo__condominio__condominio_nombre']
    inlines = [PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['pago_id', 'cuota', 'pago_fecha', 'pago_monto', 'pago_medio', 'pago_referencia']
    list_filter = ['pago_medio', 'cuota__periodo__condominio']
    search_fields = ['pago_referencia', 'cuota__unidad__unidad_numero']
    date_hierarchy = 'pago_fecha'


@admin.register(MovimientoFondo)
class MovimientoFondoAdmin(admin.ModelAdmin):
    list_display = ['movimiento_id', 'condominio', 'movimiento_tipo', 'movimiento_concepto', 'movimiento_monto', 'movimiento_fecha', 'movimiento_saldo_resultante']
    list_filter = ['movimiento_tipo', 'condominio']
    search_fields = ['movimiento_concepto', 'condominio__condominio_nombre']
    date_hierarchy = 'movimiento_fecha'


@admin.register(RegistroMorosidad)
class RegistroMorosidadAdmin(admin.ModelAdmin):
    list_display = ['morosidad_id', 'unidad', 'periodo', 'morosidad_meses', 'morosidad_monto_total', 'morosidad_activa']
    list_filter = ['morosidad_activa', 'unidad__condominio']
    search_fields = ['unidad__unidad_numero', 'unidad__condominio__condominio_nombre']


@admin.register(CorteSuministro)
class CorteSuministroAdmin(admin.ModelAdmin):
    list_display = ['corte_id', 'unidad', 'corte_fecha_habilitacion', 'corte_meses_mora', 'corte_ejecutado', 'corte_fecha_reposicion']
    list_filter = ['corte_ejecutado', 'unidad__condominio']
    search_fields = ['unidad__unidad_numero', 'unidad__condominio__condominio_nombre']
    date_hierarchy = 'corte_fecha_habilitacion'
