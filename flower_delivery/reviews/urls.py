from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:product_id>/', views.review_create, name='review_create'),
    path('list/<int:product_id>/', views.review_list, name='review_list'),
]
