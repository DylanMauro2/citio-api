from django.urls import path, include
from rest_framework import routers
from condominio_gestion import views

router = routers.DefaultRouter()
router.register(r"condominio", views.CondominioView, "condominio")
router.register(r"espacio", views.EspacioView, "espacio")
router.register(r"activo_tipo", views.ActivoTipoView, "activo_tipo")
router.register(r"activo", views.ActivoView, "activo")
router.register(r"mantencion_proveedor", views.MantencionProveedorView, "mantencion_proveedor")
router.register(r"mantencion_estado", views.MantencionEstadoView, "mantencion_estado")
router.register(r"mantencion", views.MantencionView, "mantencion")
router.register(r"mantencion_programada", views.MantencionProgramadaView, "mantencion_programada")

urlpatterns = router.urls
