from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from catalog.models import Product
from .forms import OrderForm
from bot.telegram import send_telegram_notification

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

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
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def update_order_status(request, order_id):
    if not request.user.is_staff:
        return redirect('orders:order_list')

    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            return redirect('orders:order_list')

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

            send_telegram_notification(new_order)

            return redirect('orders:order_list')
    else:
        initial_data = {
            'delivery_address': original_order.delivery_address,
            'delivery_time': original_order.delivery_time,
            'comment': original_order.comment
        }
        form = OrderForm(initial=initial_data, user=request.user, reorder_data=original_order)
    return render(request, 'orders/order_create.html', {'form': form, 'reorder': True})
