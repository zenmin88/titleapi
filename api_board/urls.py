from django.urls import path
from . import views

urlpatterns = [
    path('auth/email/', views.get_activation_code),
    path('/api/v1/auth/token/', views.get_token),
]
