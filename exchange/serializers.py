from rest_framework import serializers
from .models import User, UserDevice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'display_name',
            'profile_picture',
            'created_at',
            'updated_at',
            'last_login',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = [
            'id',
            'device_id',
            'device_name',
            'device_type',
            'is_active',
            'last_login',
        ]
        read_only_fields = ['id', 'last_login']


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication"""
    id_token = serializers.CharField(required=True, help_text='Google ID token from client')
    device_id = serializers.CharField(required=True, help_text='Unique device identifier')
    device_name = serializers.CharField(required=False, allow_blank=True, help_text='Device name')
    device_type = serializers.CharField(required=False, allow_blank=True, help_text='Device type (ios/android)')
    fcm_token = serializers.CharField(required=False, allow_blank=True, help_text='FCM token for push notifications')
