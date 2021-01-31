from django.urls import path
from . import views

urlpatterns = [
    path('auth/email/', views.get_confirmation_code),
    path('auth/token/', views.get_token),
]
