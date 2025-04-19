from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from bot.telegram import send_telegram_notification

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    try:
        # Получаем текущий статус заказа из базы данных
        old_instance = Order.objects.get(pk=instance.pk)
        # Если статус изменился, отправляем уведомление
        if old_instance.status != instance.status:
            send_telegram_notification(instance)
    except Order.DoesNotExist:
        pass  # Это новое создание заказа, не нужно отправлять уведомление
