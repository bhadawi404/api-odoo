from django.urls import path
from django.urls import re_path as url
from api.controller.base import base_controller


app_name = 'api'
urlpatterns = [
    path('<str:controllerName>/', base_controller.page, name='base_controller_all'),
    path('<str:controllerName>/<str:barcode>', base_controller.detail, name='base_controller_by_barcode'),
    path('scan/<str:controllerName>/<str:barcode>', base_controller.scan, name='base_controller_by_barcode'),
]
