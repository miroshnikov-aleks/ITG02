from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
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

            # Сохраняем товары с ценами
            for product in form.cleaned_data['products']:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=1
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
