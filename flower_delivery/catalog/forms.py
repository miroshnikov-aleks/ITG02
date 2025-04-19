from django import forms
from .models import Order, Product

class OrderForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(available=True),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Order
        fields = ['products', 'address', 'delivery_time']
