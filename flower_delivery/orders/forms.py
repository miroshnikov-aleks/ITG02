from django import forms
from .models import Order
from catalog.models import Product

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
        super().__init__(*args, **kwargs)

        if user:
            products = Product.objects.filter(available=True)
            for product in products:
                self.fields[f'quantity_{product.id}'] = forms.IntegerField(
                    min_value=1,
                    initial=1,
                    label=product.name,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )