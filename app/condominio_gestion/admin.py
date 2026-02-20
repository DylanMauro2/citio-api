from django.contrib import admin
from .models import Condominio, Espacio, ActivoTipo, Activo, MantencionEstado, Mantencion, MantencionProgramada


class EspacioInline(admin.TabularInline):
    model = Espacio
    extra = 1
    fields = ['espacio_nombre', 'espacio_descripcion', 'ubicacion_fisica', 'espacio_disponible']


class ActivoInline(admin.TabularInline):
    model = Activo
    extra = 1
    fields = ['activo_nombre', 'activo_tipo', 'activo_marca', 'activo_modelo', 'activo_estado']


@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = [
        'condominio_id',
        'condominio_nombre',
        'condominio_ubicacion',
        'condominio_activo',
        'created_at'
    ]
    list_filter = ['condominio_activo', 'created_at']
    search_fields = ['condominio_nombre', 'condominio_ubicacion']
    ordering = ['condominio_nombre']
    inlines = [EspacioInline]


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = [
        'espacio_id',
        'espacio_nombre',
        'condominio',
        'ubicacion_fisica',
        'espacio_disponible',
        'created_at'
    ]
    list_filter = ['espacio_disponible', 'condominio', 'created_at']
    search_fields = ['espacio_nombre', 'ubicacion_fisica', 'condominio__condominio_nombre']
    ordering = ['condominio', 'espacio_nombre']
    autocomplete_fields = ['condominio']
    inlines = [ActivoInline]


@admin.register(ActivoTipo)
class ActivoTipoAdmin(admin.ModelAdmin):
    list_display = ['activo_tipo_code', 'activo_tipo_nombre', 'created_at']
    search_fields = ['activo_tipo_code', 'activo_tipo_nombre']
    ordering = ['activo_tipo_nombre']


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = [
        'activo_id',
        'activo_nombre',
        'activo_tipo',
        'espacio',
        'get_condominio',
        'activo_marca',
        'activo_estado',
        'created_at'
    ]
    list_filter = ['activo_estado', 'activo_tipo', 'espacio__condominio', 'created_at']
    search_fields = [
        'activo_nombre',
        'activo_marca',
        'activo_modelo',
        'activo_numero_serie',
        'espacio__espacio_nombre',
        'espacio__condominio__condominio_nombre'
    ]
    ordering = ['espacio', 'activo_nombre']
    autocomplete_fields = ['espacio', 'activo_tipo']

    @admin.display(description='Condominio')
    def get_condominio(self, obj):
        return obj.espacio.condominio.condominio_nombre


@admin.register(MantencionEstado)
class MantencionEstadoAdmin(admin.ModelAdmin):
    list_display = ['mantencion_estado_code', 'mantencion_estado_nombre', 'created_at']
    search_fields = ['mantencion_estado_code', 'mantencion_estado_nombre']
    ordering = ['mantencion_estado_nombre']


@admin.register(Mantencion)
class MantencionAdmin(admin.ModelAdmin):
    list_display = [
        'mantencion_id',
        'activo',
        'mantencion_estado',
        'mantencion_tipo',
        'mantencion_fecha_realizacion',
        'mantencion_costo',
        'mantencion_realizada_por',
    ]
    list_filter = ['mantencion_tipo', 'mantencion_estado', 'mantencion_fecha_realizacion']
    search_fields = [
        'activo__activo_nombre',
        'mantencion_realizada_por',
        'mantencion_descripcion'
    ]
    ordering = ['-created_at']
    autocomplete_fields = ['activo']
    date_hierarchy = 'mantencion_fecha_realizacion'


@admin.register(MantencionProgramada)
class MantencionProgramadaAdmin(admin.ModelAdmin):
    list_display = [
        'mantencion_programada_id',
        'activo',
        'mantencion_estado',
        'mantencion_programada_fecha',
        'created_at',
    ]
    list_filter = ['mantencion_estado', 'mantencion_programada_fecha']
    search_fields = ['activo__activo_nombre', 'mantencion_programada_descripcion']
    ordering = ['mantencion_programada_fecha']
    autocomplete_fields = ['activo']
    date_hierarchy = 'mantencion_programada_fecha'
