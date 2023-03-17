from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('emodule.urls')),
    path('emodule/', include('emodule.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
