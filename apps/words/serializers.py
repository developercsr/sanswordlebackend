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


class MyWordsSerializer(serializers.Serializer):
    """Serializer for /api/words/my-words response format."""
    id = serializers.IntegerField()
    word = serializers.CharField()
    meaning = serializers.CharField()
    hint1 = serializers.CharField()
    hint2 = serializers.CharField()
    class_val = serializers.SerializerMethodField()
    chapter = serializers.SerializerMethodField()
    is_approved = serializers.BooleanField()
    is_rejected = serializers.BooleanField()
    created_time = serializers.DateTimeField(source='created_at')
    updated_time = serializers.DateTimeField(source='updated_at')

    def get_class_val(self, obj):
        lst = _parse_list_string(obj.class_name)
        return lst[0] if lst else ''

    def get_chapter(self, obj):
        lst = _parse_list_string(obj.chapter)
        return lst[0] if lst else ''

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['class'] = data.pop('class_val', '')
        return data


def _parse_list_string(s):
    """Safely parse a string like \"['5','6']\" into a list. Returns [] on error."""
    import ast
    if not s or not isinstance(s, str) or not s.strip():
        return []
    s = s.strip()
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return [str(x) for x in result]
        return []
    except (ValueError, SyntaxError):
        return []


def _list_to_string(lst):
    """Convert list to string format for storage."""
    return str([str(x) for x in lst])


class WordUploadSerializer(serializers.Serializer):
    """
    Handles word upload with trim, duplicate check, and class/chapter list updates.
    Accepts 'class' from request (mapped to class_num) and 'chapter'.
    All fields are mandatory.
    """
    word = serializers.CharField(max_length=255)
    meaning = serializers.CharField(required=True, allow_blank=False)
    hint1 = serializers.CharField(required=True, allow_blank=False)
    hint2 = serializers.CharField(required=True, allow_blank=False)
    class_num = serializers.CharField(required=True, allow_blank=False)
    chapter = serializers.CharField(required=True, allow_blank=False)

    def _validate_not_empty(self, value, field_name):
        if not value or not str(value).strip():
            raise serializers.ValidationError(f"{field_name} is required")
        return str(value).strip()

    def validate_word(self, value):
        """Trim word and normalize (lowercase for ASCII/English words)."""
        if not value:
            raise serializers.ValidationError("Word cannot be empty")
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Word cannot be empty")
        if trimmed.isascii() and trimmed.isalpha():
            trimmed = trimmed.lower()
        return trimmed

    def validate_meaning(self, value):
        return self._validate_not_empty(value, "Meaning")

    def validate_hint1(self, value):
        return self._validate_not_empty(value, "Hint 1")

    def validate_hint2(self, value):
        return self._validate_not_empty(value, "Hint 2")

    def validate_class_num(self, value):
        return self._validate_not_empty(value, "Class")

    def validate_chapter(self, value):
        return self._validate_not_empty(value, "Chapter")

    def create(self, validated_data):
        request = self.context['request']
        trimmed_word = validated_data['word']
        class_val = validated_data.get('class_num', '').strip()
        chapter_val = validated_data.get('chapter', '').strip()

        existing = Word.objects.filter(word=trimmed_word).first()

        if existing:
            existing_classes = _parse_list_string(existing.class_name)
            existing_chapters = _parse_list_string(existing.chapter)

            class_exists = class_val and class_val in existing_classes
            chapter_exists = chapter_val and chapter_val in existing_chapters

            if class_val and chapter_val and class_exists and chapter_exists:
                raise serializers.ValidationError(
                    "Word already exists for this class and chapter"
                )

            class_is_new = class_val and class_val not in existing_classes
            chapter_is_new = chapter_val and chapter_val not in existing_chapters

            if not class_is_new and not chapter_is_new:
                raise serializers.ValidationError(
                    "Word already exists for this class and chapter"
                )

            if class_is_new:
                if class_val not in existing_classes:
                    existing_classes.append(class_val)
                existing.class_name = _list_to_string(existing_classes)
            if chapter_is_new:
                if chapter_val not in existing_chapters:
                    existing_chapters.append(chapter_val)
                existing.chapter = _list_to_string(existing_chapters)

            existing.meaning = validated_data.get('meaning', existing.meaning) or existing.meaning
            existing.hint1 = validated_data.get('hint1', existing.hint1) or existing.hint1
            existing.hint2 = validated_data.get('hint2', existing.hint2) or existing.hint2
            existing.save()
            self._was_update = True
            return existing

        self._was_update = False
        return Word.objects.create(
            word=trimmed_word,
            meaning=validated_data.get('meaning', ''),
            hint1=validated_data.get('hint1', ''),
            hint2=validated_data.get('hint2', ''),
            class_name=_list_to_string([class_val] if class_val else []),
            chapter=_list_to_string([chapter_val] if chapter_val else []),
            uploaded_by=request.user,
            is_rejected=False,
            is_approved=False,
            approved_by=None,
        )
