from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include(('catalog.urls', 'catalog'), namespace='catalog')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)