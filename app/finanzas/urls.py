from rest_framework import routers
from finanzas import views

router = routers.DefaultRouter()
router.register(r'presupuesto', views.PresupuestoView, 'presupuesto')
router.register(r'item_presupuesto', views.ItemPresupuestoView, 'item_presupuesto')
router.register(r'periodo_cobro', views.PeriodoCobroView, 'periodo_cobro')
router.register(r'cuota_unidad', views.CuotaUnidadView, 'cuota_unidad')
router.register(r'pago', views.PagoView, 'pago')
router.register(r'movimiento_fondo', views.MovimientoFondoView, 'movimiento_fondo')
router.register(r'registro_morosidad', views.RegistroMorosidadView, 'registro_morosidad')
router.register(r'corte_suministro', views.CorteSuministroView, 'corte_suministro')

urlpatterns = router.urls
