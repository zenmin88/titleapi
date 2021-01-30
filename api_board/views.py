from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from rest_framework import views, status, serializers
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from rest_framework.reverse import reverse

from api_board.serializers import UserSerializer

User = get_user_model()


@api_view(['POST'])
def get_activation_code(request):
    """
    Register new user and sent activation code.
    For existing user sent activation code.
    """

    email = request.data.get('email')
    username = request.data.get('username')
    data = {
        'username': username,
        'email': email
    }
    serializer = UserSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
    # Create activation code and send email
    token = default_token_generator.make_token(user)
    user.email_user(subject='Activation code',
                    message='Your activation code %s ' % token
                    )

    return Response(serializer.data)

def get_token():
    pass
