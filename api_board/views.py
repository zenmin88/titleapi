from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.utils.timezone import now
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_board.serializers import CreateUserSerializer, UserSerializer, CategorySerializer, GenreSerializer, \
    TitleSerializerGet, ReviewSerializer, CommentSerializer, TitleSerializerPost
from .filters import TitleFilter
from .functions import generate_username
from .mixins import ReviewCommentMixin, CategoryGenreMixin
from .models import Category, Genre, Title, Review, Comment
from .permissions import IsAdminRole

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False,  permission_classes=[permissions.IsAuthenticated],
            methods=['GET', 'PATCH'], url_path='me', url_name='me')
    def current_user(self, request):
        serializer_class = self.get_serializer_class()

        if request.method == 'GET':
            serializer = serializer_class(request.user)
        else:
            serializer = serializer_class(instance=request.user,
                                          data=self.request.data,
                                          partial=True,
                                          context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer(self, *args, **kwargs):
        if self.action in ['list', 'retrieve']:
            serializer_class = TitleSerializerGet
        else:
            serializer_class = TitleSerializerPost
        return serializer_class(*args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminRole]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Added annotation field with average rating."""
        queryset = Title.objects.all().annotate(rating=Avg('reviews__score')).order_by('id')
        return queryset


class ReviewViewSet(ReviewCommentMixin):
    serializer_class = ReviewSerializer
    model = Review
    related_model = Title
    related_field = 'title'


class CommentViewSet(ReviewCommentMixin):
    serializer_class = CommentSerializer
    model = Comment  # Review
    related_model = Review  # Title
    related_field = 'review'  # 'title'


@api_view(['POST'])
def get_confirmation_code(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        serializer = CreateUserSerializer(instance=user)
    except User.DoesNotExist:
        username = request.data.get('username')
        if not username:
            username = generate_username(User, email)
        data = {
            'username': username,
            'email': email
        }
        serializer = CreateUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

    # Create confirmation code and send email
    confirmation_code = default_token_generator.make_token(user)  # noqa
    user.email_user(subject='Activation code',
                    message='Your confirmation code %s ' % confirmation_code
                    )

    return Response(serializer.data)


@api_view(['POST'])
def get_token(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError("Invalid email",
                              code=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, confirmation_code):

        # Creating a record about logging, after that confirmation code doesn't works
        user.last_login = now()
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response(data={'token': str(refresh.access_token)},
                        status=status.HTTP_200_OK)
    else:

        return Response(data={'confirmation_code': 'Invalid data'},
                        status=status.HTTP_400_BAD_REQUEST)
