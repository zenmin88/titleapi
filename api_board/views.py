from datetime import datetime
from random import randint

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets, filters, status, permissions, mixins
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Genre
from .permissions import IsAdminRole

from api_board.serializers import CreateUserSerializer, UserSerializer, CategorySerializer, GenreSerializer

User = get_user_model()


def generate_username(email):
    """
    Generate unique username from email
    """
    username = email.split('@')[0]
    while User.objects.filter(username=username).exists():
        username += str(randint(0, 9))
    return username


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
            username = generate_username(email)
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
    filter_backends = [filters.SearchFilter]
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


class CategoryGenreMixin(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    Mixin for category and genre
    """
    # TODO: Разобраться в необходимости слага. Можно сделать его авто генерируемым.
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsAdminRole()]
        return [permissions.AllowAny()]


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
