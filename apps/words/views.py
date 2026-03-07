"""
Word CRUD views with role-based permissions.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Word
from .serializers import WordSerializer, WordCreateSerializer, WordUpdateSerializer
from .permissions import IsWordUploader, IsWordChecker, IsWordManager
from core.utils import success_response


class WordListCreateView(APIView):
    """List words (with search/filter) and upload word."""
    permission_classes = [IsAuthenticated, IsWordUploader]

    def get(self, request):
        """List words with search and filter by verified/unverified."""
        qs = Word.objects.all().select_related('uploaded_by', 'verified_by')
        search = request.query_params.get('search')
        is_verified = request.query_params.get('is_verified')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if search:
            qs = qs.filter(
                Q(word__icontains=search) |
                Q(meaning__icontains=search)
            )
        if is_verified is not None:
            if is_verified.lower() in ('true', '1', 'yes'):
                qs = qs.filter(is_verified=True)
            elif is_verified.lower() in ('false', '0', 'no'):
                qs = qs.filter(is_verified=False)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        words = qs[start:end]
        serializer = WordSerializer(words, many=True)

        return Response(success_response({
            'items': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
        }, "Words retrieved successfully"))

    def post(self, request):
        """Upload a new word (word_uploader, word_checker, word_manager, admin)."""
        serializer = WordCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            word = Word.objects.get(pk=serializer.instance.pk)
            return Response(
                success_response(WordSerializer(word).data, "Word uploaded successfully"),
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class WordDetailView(APIView):
    """Retrieve, update, delete word."""
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsWordManager()]
        return [IsAuthenticated(), IsWordUploader()]

    def get_object(self, pk):
        try:
            return Word.objects.select_related('uploaded_by', 'verified_by').get(pk=pk)
        except Word.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Word not found")

    def get(self, request, pk):
        """Get word by ID."""
        word = self.get_object(pk)
        serializer = WordSerializer(word)
        return Response(success_response(serializer.data, "Word retrieved successfully"))

    def put(self, request, pk):
        """Update word (word_manager or admin)."""
        word = self.get_object(pk)
        serializer = WordUpdateSerializer(word, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(success_response(WordSerializer(word).data, "Word updated successfully"))
        return Response(
            {"success": False, "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Delete word (word_manager or admin)."""
        word = self.get_object(pk)
        word.delete()
        return Response(success_response(None, "Word deleted successfully"), status=status.HTTP_200_OK)


class WordVerifyView(APIView):
    """Verify word (word_checker, word_manager, admin)."""
    permission_classes = [IsAuthenticated, IsWordChecker]

    def post(self, request, pk):
        """Mark word as verified."""
        try:
            word = Word.objects.get(pk=pk)
        except Word.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Word not found")

        from django.utils import timezone
        word.is_verified = True
        word.verified_by = request.user
        word.verified_at = timezone.now()
        word.save()
        serializer = WordSerializer(word)
        return Response(success_response(serializer.data, "Word verified successfully"))
