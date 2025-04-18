from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order
from bot.telegram import send_telegram_notification

@receiver(pre_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    try:
        old_instance = Order.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            send_telegram_notification(instance)
    except Order.DoesNotExist:
        pass  # Это новое создание заказа, не нужно отправлять уведомление
