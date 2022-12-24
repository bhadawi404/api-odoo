
from django.urls import path, include
from user_management.views import UserRegistrationView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
]