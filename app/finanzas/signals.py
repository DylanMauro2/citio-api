from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def _recalcular_total(presupuesto):
    total = presupuesto.items.aggregate(total=Sum('item_monto_mensual'))['total'] or 0
    presupuesto.__class__.objects.filter(pk=presupuesto.pk).update(presupuesto_monto_total=total)


@receiver(post_save, sender='finanzas.ItemPresupuesto')
def on_item_guardado(sender, instance, **kwargs):
    _recalcular_total(instance.presupuesto)


@receiver(post_delete, sender='finanzas.ItemPresupuesto')
def on_item_eliminado(sender, instance, **kwargs):
    _recalcular_total(instance.presupuesto)
