from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

route = SimpleRouter()
route.register(r'users', views.UserViewSet, basename='user')
route.register(r'categories', views.CategoryViewSet, basename='category')
route.register(r'genres', views.GenreViewSet, basename='genre')
route.register(r'titles', views.TitleViewSet, basename='title')
route.register(r'titles/(?P<title_id>[^/.]+)/reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('auth/email/', views.get_confirmation_code),
    path('auth/token/', views.get_token),
    path('role/', views.check_role),
    path('', include(route.urls))
]
