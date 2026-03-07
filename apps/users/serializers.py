"""
Serializers for User model.
Profile: own only, role is read-only (not editable by self).
User CRUD: hierarchy-based, can only assign lower-level roles.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .hierarchy import can_assign_role, assignable_roles

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User - includes status, deactivated_by, timestamps."""

    created_by_name = serializers.SerializerMethodField()
    deactivated_by_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def get_deactivated_by_name(self, obj):
        return obj.deactivated_by.full_name if obj.deactivated_by else None

    def get_status(self, obj):
        return 'active' if obj.is_active else 'inactive'

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'mobile_number', 'school',
            'role', 'status', 'is_active', 'created_by', 'created_by_name',
            'deactivated_by', 'deactivated_by_name', 'deactivated_at',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'deactivated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Create user - can only assign lower-level roles."""

    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['full_name', 'email', 'mobile_number', 'school', 'role', 'password']

    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            return value
        if not can_assign_role(request.user, value):
            assignable = assignable_roles(request.user)
            raise serializers.ValidationError(
                f"You can only assign lower-level roles: {assignable}"
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        request = self.context.get('request')
        user = User(**validated_data)
        user.set_password(password)
        if request and request.user:
            user.created_by = request.user
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user - role and is_active editable only by higher-level users."""

    class Meta:
        model = User
        fields = ['full_name', 'mobile_number', 'school', 'role', 'is_active']

    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            return value
        if not can_assign_role(request.user, value):
            assignable = assignable_roles(request.user)
            raise serializers.ValidationError(
                f"You can only assign lower-level roles: {assignable}"
            )
        return value

    def update(self, instance, validated_data):
        """On reactivation, clear deactivated_by and deactivated_at."""
        from django.utils import timezone
        is_active = validated_data.get('is_active')
        if is_active and not instance.is_active:
            validated_data['deactivated_by'] = None
            validated_data['deactivated_at'] = None
        elif not is_active and instance.is_active:
            request = self.context.get('request')
            if request and request.user:
                validated_data['deactivated_by'] = request.user
                validated_data['deactivated_at'] = timezone.now()
        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """Profile - own only. Role is read-only (not part of editable profile)."""

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return 'active' if obj.is_active else 'inactive'

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'mobile_number', 'school',
            'role', 'status', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at', 'last_login']
