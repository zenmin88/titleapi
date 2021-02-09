from django.contrib import admin

from api_board.models import Genre, Category, Title


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

