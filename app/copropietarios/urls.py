from rest_framework import routers
from copropietarios import views

router = routers.DefaultRouter()
router.register(r'unidad', views.UnidadView, 'unidad')
router.register(r'persona', views.PersonaView, 'persona')
router.register(r'registro_tenencia', views.RegistroTenenciaView, 'registro_tenencia')

urlpatterns = router.urls
