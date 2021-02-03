from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
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
    """
    API endpoint(user/) that allow only admin get,post,patch and delete data.
    API endpoint(me/) that allow only request.user get and post data.
    User cannot change role attribute.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username']

    @action(detail=False,  permission_classes=[permissions.IsAuthenticated],
            methods=['GET', 'PATCH'], url_path='me', url_name='me')
    def current_user(self, request):
        """
        Get current user info.
        Update current user info.
        """
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
    """
    API endpoint that allows all users to be viewed,
    only admin can edit and delete.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    """
    API endpoint that allows all users to be viewed,
    only admin can edit and delete.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Api endpoint all users can view it,
    but only admin can create, update and delete it.
    """
    queryset = Title.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TitleFilter

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
        """
        Added annotation field with average rating
        """
        queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
        return queryset

    # def get_queryset(self):
    #     """
    #     Filter query set wit Q objects
    #     """
    #     # TODO: DEL
    #     queryset = Title.objects.all()
    #     filter_dict = {
    #         'name': lambda x: Q(name__icontains=x),
    #         'year': lambda x: Q(year__exact=x),
    #         'genre': lambda x: Q(genre__slug__exact=x),
    #         'category': lambda x: Q(category__slug__exact=x)
    #     }
    #
    #     for key, value in self.request.query_params.items():
    #         custom_filter = filter_dict.get(key)
    #         if custom_filter:
    #             queryset = queryset.filter(custom_filter(value))
    #     return queryset.annotate(rating=Avg('reviews__score'))


class ReviewViewSet(ReviewCommentMixin):
    """
    Api endpoint where users can publishing their review and view it.
    Admin, moderator and author of review can update and destroy it.
    """
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
    """
    Register new user and sent activation code.
    For existing user sent activation code.
    """
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
    """
    Get token for user
    """
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError("Invalid email",
                              code=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, confirmation_code):
        # Creating a record about logging, after that confirmation code doesn't works
        user.last_login = datetime.now()
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response(data={'token': str(refresh.access_token)},
                        status=status.HTTP_200_OK)
    else:

        return Response(data={'confirmation_code': 'Invalid data'},
                        status=status.HTTP_400_BAD_REQUEST)
