from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

route = SimpleRouter()
route.register(r'users', views.UserViewSet, basename='user')
route.register(r'categories', views.CategoryViewSet, basename='category')
route.register(r'genres', views.GenreViewSet, basename='genre')

urlpatterns = [
    path('auth/email/', views.get_confirmation_code),
    path('auth/token/', views.get_token),
    path('', include(route.urls))
]
