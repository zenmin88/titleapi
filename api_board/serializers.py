from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework import serializers, status

from api_board.functions import generate_slug
from api_board.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'email', 'role']

    def update(self, instance, validated_data):
        """
        Checks that only the admin can change the role
        """
        user = self.context['request'].user

        if validated_data.get('role', False) and user.role != 'admin' and not user.is_superuser:
            raise exceptions.PermissionDenied(detail={"role": "Only admin can change role"},

                                              code=status.HTTP_403_FORBIDDEN)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']

    def create(self, validated_data):
        validated_data['slug'] = generate_slug(validated_data, Category)
        category = Category.objects.create(**validated_data)
        return category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']
        ordering = ['name']

    def create(self, validated_data):
        validated_data['slug'] = generate_slug(validated_data, Genre)
        genre = Genre.objects.create(**validated_data)
        return genre


class TitleSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    # TODO: uncomment
    # rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'rating', 'description', 'genre', 'category']
        ordering = ['id']


class TitleSerializerPost(TitleSerializerGet):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug',
                                            many=False,
                                            )
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug',
                                         many=True,
                                         )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(many=False,
                                          read_only=True,
                                          slug_field='username')
    title = serializers.SlugRelatedField(many=False,
                                         read_only=True,
                                         slug_field='name')

    class Meta:
        model = Review
        fields = ['id', 'author', 'title', 'text', 'score', 'pub_date']

    def validate(self, attrs):
        """
        Validate every author can create only one review
        """
        author = self.context['request'].user
        title = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title) and self.context['request'].method == 'POST':
            raise serializers.ValidationError("For each title the user can create only one review")
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(many=False,
                                          read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
