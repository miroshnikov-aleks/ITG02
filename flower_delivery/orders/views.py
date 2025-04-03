from django.shortcuts import render, redirect
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
                if field_name.startswith('quantity_'):
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