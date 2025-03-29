from django import forms
from .models import Order
from catalog.models import Product

class OrderForm(forms.ModelForm):
    """Форма для создания заказа."""
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(available=True),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_time', 'comment']  # Добавили комментарий
        widgets = {
            'delivery_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите полный адрес доставки'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные пожелания к заказу...'
            })
        }
        labels = {
            'delivery_address': 'Адрес доставки',
            'delivery_time': 'Дата и время доставки',
            'comment': 'Комментарий к заказу'  # Добавили метку
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['products'].queryset = Product.objects.filter(available=True)