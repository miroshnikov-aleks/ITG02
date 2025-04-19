from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')
    list_filter = ('available',)
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin)
