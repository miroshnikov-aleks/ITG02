from django import forms
from .models import Order
from catalog.models import Product
from django.utils import timezone
from django.core.exceptions import ValidationError
import pytz

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_time', 'comment']
        widgets = {
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите полный адрес доставки'
            }),
            'delivery_time': forms.DateTimeInput(attrs={
                'class': 'form-control datetimepicker',
                'type': 'datetime-local'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные пожелания...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        reorder_data = kwargs.pop('reorder_data', None)
        super().__init__(*args, **kwargs)
        if user:
            products = Product.objects.filter(available=True)
            for product in products:
                initial_quantity = 0
                if reorder_data:
                    order_item = reorder_data.items.filter(product=product).first()
                    if order_item:
                        initial_quantity = order_item.quantity
                self.fields[f'quantity_{product.id}'] = forms.IntegerField(
                    min_value=0,
                    initial=initial_quantity,
                    label=product.name,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
    
    def clean_delivery_time(self):
        delivery_time = self.cleaned_data.get('delivery_time')
        if delivery_time:
            # Преобразуем время в местное время Москвы
            moscow_tz = pytz.timezone('Europe/Moscow')
            delivery_time = timezone.localtime(delivery_time, moscow_tz)
            
            # Проверяем рабочее время
            if not (9 <= delivery_time.hour < 18):
                raise ValidationError("Заказы принимаются только с 9:00 до 18:00")
            
            # Проверяем, что время доставки не в прошлом
            now = timezone.now()
            # Добавляем небольшой буфер времени (например, 5 секунд) для учета возможных задержек
            if delivery_time < (now + timezone.timedelta(seconds=5)):
                raise ValidationError("Время доставки должно быть не ранее чем через 5 секунд от текущего времени")
        
        return delivery_time