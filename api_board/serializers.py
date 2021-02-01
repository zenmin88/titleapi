from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework import serializers, status

from api_board.models import Category, Genre, Title

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'email', 'role']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # If user(not admin) will try to change a role  raise exception
        if validated_data.get('role', False) and user.role != 'admin' and not user.is_superuser:
            raise exceptions.PermissionDenied(detail={"role": "Only admin can change role"},

                                              code=status.HTTP_403_FORBIDDEN)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug',
                                            many=False,
                                            )
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug',
                                         many=True,
                                         )

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
