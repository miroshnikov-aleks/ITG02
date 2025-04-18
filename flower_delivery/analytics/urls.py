from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.daily_report_list, name='daily_report_list'),
]
