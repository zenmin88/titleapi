from django.contrib import admin

from api_board.models import Genre, Category, Title, User


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    ordering = ('id', 'name')
    search_fields = ('name', )
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    ordering = ('id', 'name')
    search_fields = ('name', )
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category')
    list_display_links = ('name',)
    ordering = ('id', 'name', 'year')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'role', 'first_name', 'last_name', 'bio',
              ('is_superuser', 'is_staff', 'is_active'), 'user_permissions',
              'groups', 'last_login')

    list_display = ('id', 'username', 'email', 'role')
    list_display_links = ('username',)
    list_filter = ('role', )
