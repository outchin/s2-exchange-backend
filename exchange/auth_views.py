import json
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserDevice
from .serializers import UserSerializer, GoogleAuthSerializer


@csrf_exempt
@require_http_methods(["POST"])
def google_auth(request):
    """
    Authenticate user with Google ID token

    Expected POST data:
    {
        "id_token": "google_id_token_string"
    }

    Returns:
    {
        "success": true,
        "user": {
            "email": "user@example.com",
            "display_name": "User Name",
            "profile_picture": "https://..."
        }
    }
    """
    try:
        data = json.loads(request.body)
        token = data.get('id_token')

        if not token:
            return JsonResponse({
                'success': False,
                'error': 'ID token is required'
            }, status=400)

        # Verify the Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            # ID token is valid, get user info
            google_user_id = idinfo['sub']
            email = idinfo.get('email')
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')

            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email not provided by Google'
                }, status=400)

            # Get or create user
            user, created = User.objects.get_or_create(
                google_id=google_user_id,
                defaults={
                    'email': email,
                    'display_name': name,
                    'profile_picture': picture,
                }
            )

            # Update user info if not created
            if not created:
                user.display_name = name
                user.profile_picture = picture
                user.save(update_fields=['display_name', 'profile_picture'])

            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'display_name': user.display_name,
                    'profile_picture': user.profile_picture,
                    'is_staff': user.is_staff,
                },
                'is_new_user': created,
            })

        except ValueError as e:
            # Invalid token
            return JsonResponse({
                'success': False,
                'error': f'Invalid token: {str(e)}'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def current_user(request):
    """
    Get current authenticated user info

    Returns:
    {
        "authenticated": true,
        "user": {
            "email": "user@example.com",
            "display_name": "User Name",
            "profile_picture": "https://..."
        }
    }
    """
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'display_name': request.user.display_name,
                'profile_picture': request.user.profile_picture,
                'is_staff': request.user.is_staff,
            }
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'user': None
        })


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """
    Logout current user

    Returns:
    {
        "success": true
    }
    """
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({
        'success': True
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_mobile(request):
    """
    Google OAuth authentication for mobile with JWT and single device login

    POST /api/auth/google/mobile/
    {
        "id_token": "google_id_token",
        "device_id": "unique_device_id",
        "device_name": "iPhone 12",
        "device_type": "ios",
        "fcm_token": "firebase_token"
    }

    Returns:
    {
        "success": true,
        "access_token": "jwt_access_token",
        "refresh_token": "jwt_refresh_token",
        "user": {...},
        "is_new_user": false,
        "previous_device_logged_out": false
    }
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    id_token_str = serializer.validated_data['id_token']
    device_id = serializer.validated_data['device_id']
    device_name = serializer.validated_data.get('device_name', '')
    device_type = serializer.validated_data.get('device_type', '')
    fcm_token = serializer.validated_data.get('fcm_token', '')

    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_OAUTH2_CLIENT_ID if settings.GOOGLE_OAUTH2_CLIENT_ID else None
        )

        google_user_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        if not email:
            return Response(
                {'success': False, 'error': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create user
        user, is_new_user = User.objects.get_or_create(
            google_id=google_user_id,
            defaults={
                'email': email,
                'display_name': name,
                'profile_picture': picture,
            }
        )

        # Update user info
        if not is_new_user:
            user.display_name = name
            user.profile_picture = picture
            user.last_login = timezone.now()
            user.save(update_fields=['display_name', 'profile_picture', 'last_login'])
        else:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        # Single device login: Deactivate all other devices
        previous_device_logged_out = user.devices.filter(is_active=True).exclude(
            device_id=device_id
        ).exists()

        user.devices.filter(is_active=True).exclude(device_id=device_id).update(
            is_active=False
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Get or create device
        user_device, _ = UserDevice.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'device_name': device_name,
                'device_type': device_type,
                'fcm_token': fcm_token,
                'is_active': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
        )

        return Response({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSerializer(user).data,
            'is_new_user': is_new_user,
            'previous_device_logged_out': previous_device_logged_out,
        })

    except ValueError as e:
        return Response(
            {'success': False, 'error': f'Invalid token: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': f'Server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_mobile(request):
    """
    Logout mobile device

    POST /api/auth/logout/mobile/
    {
        "device_id": "unique_device_id"
    }
    """
    device_id = request.data.get('device_id')

    if device_id:
        UserDevice.objects.filter(
            user=request.user,
            device_id=device_id
        ).update(is_active=False)

    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_mobile(request):
    """Get current authenticated user for mobile"""
    return Response({
        'success': True,
        'user': UserSerializer(request.user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account_mobile(request):
    """
    Delete user account permanently (hard delete)
    Required by Google Play Store and App Store policies

    POST /api/auth/delete-account/mobile/
    {
        "device_id": "unique_device_id",
        "confirmation": "DELETE"
    }

    Returns:
    {
        "success": true,
        "message": "Account deleted successfully"
    }
    """
    device_id = request.data.get('device_id')
    confirmation = request.data.get('confirmation')

    # Require explicit confirmation
    if confirmation != 'DELETE':
        return Response(
            {
                'success': False,
                'error': 'Please confirm account deletion by sending "DELETE" as confirmation'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        # Log the deletion for audit purposes
        from django.utils import timezone
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Account deletion requested - User ID: {user.id}, Email: {user.email}, Device: {device_id}, Time: {timezone.now()}')

        # Deactivate all user devices first
        UserDevice.objects.filter(user=user).update(is_active=False)

        # Hard delete the user account and all related data
        # Django's CASCADE will automatically delete related UserDevice records
        user.delete()

        logger.info(f'Account deleted successfully - Email: {user.email}')

        return Response({
            'success': True,
            'message': 'Your account has been permanently deleted. All your data has been removed from our servers.'
        })

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Account deletion failed - User ID: {user.id}, Error: {str(e)}')

        return Response(
            {
                'success': False,
                'error': f'Failed to delete account: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
