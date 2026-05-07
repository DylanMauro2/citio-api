from rest_framework import serializers
from .models import (
    Presupuesto, ItemPresupuesto, PeriodoCobro,
    CuotaUnidad, Pago, MovimientoFondo,
    RegistroMorosidad, CorteSuministro,
)


class ItemPresupuestoSerializer(serializers.ModelSerializer):
    item_tipo_display = serializers.CharField(source='get_item_tipo_display', read_only=True)

    class Meta:
        model = ItemPresupuesto
        fields = '__all__'
        read_only_fields = ['item_id', 'created_at', 'updated_at']


class ItemPresupuestoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPresupuesto
        fields = ['presupuesto', 'item_concepto', 'item_tipo', 'item_monto_mensual', 'item_descripcion']


class PresupuestoSerializer(serializers.ModelSerializer):
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)
    items = ItemPresupuestoSerializer(many=True, read_only=True)

    class Meta:
        model = Presupuesto
        fields = '__all__'
        read_only_fields = ['presupuesto_id', 'created_at', 'updated_at']


class PresupuestoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = [
            'condominio', 'presupuesto_anio', 'presupuesto_monto_total',
            'presupuesto_aprobado', 'presupuesto_fecha_aprobacion', 'presupuesto_activo',
        ]


class PeriodoCobroSerializer(serializers.ModelSerializer):
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)

    class Meta:
        model = PeriodoCobro
        fields = '__all__'
        read_only_fields = ['periodo_id', 'created_at', 'updated_at']


class PeriodoCobroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoCobro
        fields = [
            'condominio', 'presupuesto', 'periodo_mes', 'periodo_anio',
            'periodo_fecha_vencimiento', 'periodo_cerrado',
        ]


class PagoSerializer(serializers.ModelSerializer):
    pago_medio_display = serializers.CharField(source='get_pago_medio_display', read_only=True)

    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ['pago_id', 'created_at']


class PagoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['cuota', 'pago_fecha', 'pago_monto', 'pago_medio', 'pago_referencia', 'pago_registrado_por']


class CuotaUnidadSerializer(serializers.ModelSerializer):
    unidad_numero = serializers.CharField(source='unidad.unidad_numero', read_only=True)
    condominio_nombre = serializers.CharField(source='unidad.condominio.condominio_nombre', read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)

    class Meta:
        model = CuotaUnidad
        fields = '__all__'
        read_only_fields = ['cuota_id', 'created_at', 'updated_at']


class CuotaUnidadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaUnidad
        fields = [
            'periodo', 'unidad', 'cuota_monto_ordinario', 'cuota_monto_extraordinario',
            'cuota_interes_mora', 'cuota_saldo_pendiente', 'cuota_pagada',
        ]


class MovimientoFondoSerializer(serializers.ModelSerializer):
    condominio_nombre = serializers.CharField(source='condominio.condominio_nombre', read_only=True)
    movimiento_tipo_display = serializers.CharField(source='get_movimiento_tipo_display', read_only=True)

    class Meta:
        model = MovimientoFondo
        fields = '__all__'
        read_only_fields = ['movimiento_id', 'created_at']


class MovimientoFondoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoFondo
        fields = [
            'condominio', 'mantencion', 'movimiento_tipo', 'movimiento_concepto',
            'movimiento_monto', 'movimiento_fecha', 'movimiento_saldo_resultante',
        ]


class RegistroMorosidadSerializer(serializers.ModelSerializer):
    unidad_numero = serializers.CharField(source='unidad.unidad_numero', read_only=True)
    condominio_nombre = serializers.CharField(source='unidad.condominio.condominio_nombre', read_only=True)

    class Meta:
        model = RegistroMorosidad
        fields = '__all__'
        read_only_fields = ['morosidad_id', 'created_at', 'updated_at']


class RegistroMorosidadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroMorosidad
        fields = ['unidad', 'periodo', 'morosidad_meses', 'morosidad_monto_total', 'morosidad_activa']


class CorteSuministroSerializer(serializers.ModelSerializer):
    unidad_numero = serializers.CharField(source='unidad.unidad_numero', read_only=True)
    condominio_nombre = serializers.CharField(source='unidad.condominio.condominio_nombre', read_only=True)

    class Meta:
        model = CorteSuministro
        fields = '__all__'
        read_only_fields = ['corte_id', 'created_at', 'updated_at']


class CorteSuministroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorteSuministro
        fields = [
            'unidad', 'corte_fecha_habilitacion', 'corte_acuerdo_asamblea',
            'corte_meses_mora', 'corte_ejecutado', 'corte_fecha_reposicion',
        ]
