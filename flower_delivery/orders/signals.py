from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from bot.telegram import send_order_notification

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    try:
        old_instance = Order.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            send_order_notification(instance.pk, is_new=False)
    except Order.DoesNotExist:
        pass