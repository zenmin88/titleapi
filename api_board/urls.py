from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

route = SimpleRouter()
route.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('auth/email/', views.get_confirmation_code),
    path('auth/token/', views.get_token),
    path('', include(route.urls))
]
