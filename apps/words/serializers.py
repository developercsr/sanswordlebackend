"""
Serializers for Word model.
"""
from rest_framework import serializers
from .models import Word


class WordSerializer(serializers.ModelSerializer):
    """Serializer for Word - includes added_by, added_at, verified_at, etc."""
    uploaded_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    added_at = serializers.DateTimeField(source='created_at', read_only=True)
    added_by = serializers.IntegerField(source='uploaded_by_id', read_only=True, allow_null=True)
    added_by_name = serializers.SerializerMethodField()

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None

    def get_added_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None

    def get_verified_by_name(self, obj):
        return obj.verified_by.full_name if obj.verified_by else None

    class Meta:
        model = Word
        fields = [
            'id', 'word', 'meaning', 'hint1', 'hint2', 'length',
            'uploaded_by', 'uploaded_by_name', 'added_by', 'added_by_name', 'added_at',
            'verified_by', 'verified_by_name', 'verified_at',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'length', 'created_at', 'updated_at', 'verified_at']


class WordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating words - length auto-calculated."""

    class Meta:
        model = Word
        fields = ['word', 'meaning', 'hint1', 'hint2']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class WordUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating words."""

    class Meta:
        model = Word
        fields = ['word', 'meaning', 'hint1', 'hint2']
