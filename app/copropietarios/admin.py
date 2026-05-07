from django.contrib import admin
from .models import Unidad, Persona, RegistroTenencia


class TenenciaInline(admin.TabularInline):
    model = RegistroTenencia
    extra = 0
    fields = ['persona', 'tenencia_tipo', 'tenencia_fecha_inicio', 'tenencia_fecha_termino', 'tenencia_activa']
    autocomplete_fields = ['persona']


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = [
        'unidad_id',
        'condominio',
        'unidad_numero',
        'unidad_block',
        'unidad_piso',
        'unidad_tipo',
        'unidad_activa',
        'created_at',
    ]
    list_filter = ['unidad_tipo', 'unidad_activa', 'condominio']
    search_fields = ['unidad_numero', 'unidad_block', 'condominio__condominio_nombre', 'unidad_rol_sii']
    ordering = ['condominio', 'unidad_block', 'unidad_piso', 'unidad_numero']
    autocomplete_fields = ['condominio']
    inlines = [TenenciaInline]


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = [
        'persona_id',
        'persona_nombre',
        'persona_rut',
        'persona_email',
        'persona_telefono',
        'created_at',
    ]
    search_fields = ['persona_nombre', 'persona_rut', 'persona_email']
    ordering = ['persona_nombre']


@admin.register(RegistroTenencia)
class RegistroTenenciaAdmin(admin.ModelAdmin):
    list_display = [
        'registro_id',
        'persona',
        'unidad',
        'tenencia_tipo',
        'tenencia_fecha_inicio',
        'tenencia_fecha_termino',
        'tenencia_activa',
    ]
    list_filter = ['tenencia_tipo', 'tenencia_activa', 'unidad__condominio']
    search_fields = [
        'persona__persona_nombre',
        'persona__persona_rut',
        'unidad__unidad_numero',
        'unidad__condominio__condominio_nombre',
    ]
    ordering = ['-tenencia_fecha_inicio']
    autocomplete_fields = ['unidad', 'persona']
    date_hierarchy = 'tenencia_fecha_inicio'
