"""Auth API: register, login, logout. Returns token for Authorization header."""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def _auth_response(user, token):
    return {
        'token': token.key,
        'user': {'id': user.id, 'email': user.email, 'name': user.first_name or user.email},
    }


# Swagger: request body with example so UI shows clean JSON to edit
_register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Full name'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password (min 6 characters)'),
    },
    example={'name': 'Admin', 'email': 'admin@example.com', 'password': 'SecurePass123'},
)
_login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
    },
    example={'email': 'admin@example.com', 'password': 'SecurePass123'},
)
_auth_resp = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='Use in header: Authorization: Token <token>'),
        'user': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        }),
    },
)


@swagger_auto_schema(
    method='post',
    operation_summary='Register new user',
    operation_description='Create an account. Returns **token** and **user**. Use the token in `Authorization: Token <token>` for other APIs.',
    request_body=_register_schema,
    responses={201: openapi.Response('Created', _auth_resp), 400: 'Bad Request'},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    email = (data.get('email') or '').strip()
    password = data.get('password')
    name = (data.get('name') or '').strip()

    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({'detail': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'detail': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=email).exists():
        return Response({'detail': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
    except IntegrityError:
        return Response({'detail': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        if getattr(e, 'messages', None):
            msg = e.messages[0] if isinstance(e.messages[0], str) else str(e.messages[0])
        elif getattr(e, 'message_dict', None):
            first = next(iter(e.message_dict.values()), None)
            msg = first[0] if first and isinstance(first, list) else str(first) if first else 'Password does not meet requirements.'
        else:
            msg = str(e) if e else 'Password does not meet requirements.'
        return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)
    return Response(_auth_response(user, token), status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_summary='Log in',
    operation_description='Returns **token** and **user**. Use the token in `Authorization: Token <token>` for other APIs.',
    request_body=_login_schema,
    responses={200: openapi.Response('OK', _auth_resp), 401: 'Unauthorized'},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user or not authenticate(request, username=user.username, password=password):
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response(_auth_response(user, token))


@swagger_auto_schema(
    method='post',
    operation_summary='Log out',
    operation_description='Invalidates the current token. Send **Authorization: Token &lt;your_token&gt;**.',
    responses={200: 'OK', 401: 'Unauthorized'},
)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({'detail': 'Logged out successfully.'})
