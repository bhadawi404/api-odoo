from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url

urlpatterns = [
    path("api/v1/", include("api.urls")),
    path('admin/', admin.site.urls),
    path('api/user/', include('user_management.urls'))
]
