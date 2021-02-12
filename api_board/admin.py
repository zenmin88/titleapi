from django.contrib import admin
from django.utils.text import Truncator

from api_board.models import Genre, Category, Title, User, Review, Comment


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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_text', 'score', 'author', 'pub_date', 'title')
    list_display_links = ('truncated_text',)
    ordering = ('id', 'pub_date')
    list_filter = ('score', )
    search_fields = ('text', )

    @staticmethod
    def truncated_text(obj):
        return Truncator(obj.text).chars(120)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'pub_date', 'review', 'title')
    list_display_links = ('text', )
    ordering = ('author', 'review', 'pub_date')

    @staticmethod
    def title(obj):
        return obj.review.title.name
