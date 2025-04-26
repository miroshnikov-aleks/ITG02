from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Order, OrderItem
from catalog.models import Product
from .forms import OrderForm
from bot.telegram import send_telegram_notification
from analytics.models import DailyReport
from decimal import Decimal
from django.http import HttpResponseForbidden

def update_daily_report(order):
    today = timezone.now().date()
    report, created = DailyReport.objects.get_or_create(date=today)
    report.order_count += 1
    report.total_revenue = Decimal(str(report.total_revenue)) + order.total_price
    report.save()

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Обрабатываем только товары с quantity > 0
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('quantity_') and value > 0:
                    product_id = field_name.split('_')[1]
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=value
                    )

            # Проверяем, что в заказе есть товары
            if order.items.count() == 0:
                order.delete()
                form.add_error(None, "Выберите хотя бы один товар")
                return render(request, 'orders/order_create.html', {'form': form})

            update_daily_report(order)
            send_telegram_notification(order)
            return redirect('orders:order_list')
    else:
        form = OrderForm(user=request.user)
    return render(request, 'orders/order_create.html', {'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user and not request.user.is_staff:
        raise PermissionDenied("У вас нет доступа к этому заказу")
    return render(request, 'orders/order_detail.html', {'order': order})

@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            send_telegram_notification(order)
            return redirect('orders:all_orders')

    return render(request, 'orders/update_order_status.html', {'order': order})

@login_required
def reorder(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user, reorder_data=original_order)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.user = request.user
            new_order.save()

            # Добавляем товары
            items_added = False
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('quantity_') and value > 0:
                    product_id = field_name.split('_')[1]
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=new_order,
                        product=product,
                        price=product.price,
                        quantity=value
                    )
                    items_added = True

            if not items_added:
                new_order.delete()
                form.add_error(None, "Выберите хотя бы один товар")
                return render(request, 'orders/order_create.html', {'form': form, 'reorder': True})

            update_daily_report(new_order)
            send_telegram_notification(new_order)
            return redirect('orders:order_list')
    else:
        initial_data = {
            'delivery_address': original_order.delivery_address,
            'delivery_time': original_order.delivery_time.strftime('%Y-%m-%dT%H:%M'),
            'comment': original_order.comment
        }
        form = OrderForm(initial=initial_data, user=request.user, reorder_data=original_order)

    return render(request, 'orders/order_create.html', {'form': form, 'reorder': True})

@user_passes_test(lambda u: u.is_staff)
def all_orders(request):
    orders = Order.objects.all().prefetch_related('items')
    return render(request, 'orders/all_orders.html', {'orders': orders})
