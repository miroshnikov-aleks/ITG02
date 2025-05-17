from django.contrib import admin
from .models import Order, OrderItem
from bot.telegram import send_order_notification

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at']
    actions = ['mark_as_in_progress', 'mark_as_in_delivery', 'mark_as_completed', 'mark_as_canceled', 'delete_selected_orders']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            send_order_notification(obj.pk, is_new=False)

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        for order in queryset:
            send_order_notification(order.pk, is_new=False)
    mark_as_in_progress.short_description = "Отметить как в обработке"

    def mark_as_in_delivery(self, request, queryset):
        queryset.update(status='in_delivery')
        for order in queryset:
            send_order_notification(order.pk, is_new=False)
    mark_as_in_delivery.short_description = "Отметить как в доставке"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        for order in queryset:
            send_order_notification(order.pk, is_new=False)
    mark_as_completed.short_description = "Отметить как выполнен"

    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')
        for order in queryset:
            send_order_notification(order.pk, is_new=False)
    mark_as_canceled.short_description = "Отметить как отменен"

    def delete_selected_orders(self, request, queryset):
        queryset.delete()
    delete_selected_orders.short_description = "Удалить выбранные заказы"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']