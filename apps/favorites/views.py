"""
Favorites API: get, add, remove.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import UserFavoriteWords


def _get_or_create_favorites(user):
    obj, _ = UserFavoriteWords.objects.get_or_create(
        user=user,
        defaults={'favorite_data': {}}
    )
    return obj


def _ensure_structure(data, class_val, chapter_val, length_str):
    ck = str(class_val)
    chk = str(chapter_val)
    if ck not in data:
        data[ck] = {}
    if chk not in data[ck]:
        data[ck][chk] = {}
    for i in range(1, 6):
        k = str(i)
        if k not in data[ck][chk]:
            data[ck][chk][k] = []
    return data


class FavoritesGetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        obj = _get_or_create_favorites(request.user)
        return Response({'favorites': obj.favorite_data})


class FavoritesAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        class_val = request.data.get('class')
        chapter_val = request.data.get('chapter')
        word_id = request.data.get('word_id')
        word_length = request.data.get('word_length')
        if class_val is None or chapter_val is None or word_id is None or word_length is None:
            return Response(
                {'status': 'error', 'message': 'Missing class, chapter, word_id, or word_length'},
                status=status.HTTP_400_BAD_REQUEST
            )
        class_val, chapter_val = str(class_val), str(chapter_val)
        length_str = str(word_length)
        if length_str not in ('1', '2', '3', '4', '5'):
            return Response(
                {'status': 'error', 'message': 'word_length must be 1-5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj = _get_or_create_favorites(request.user)
        data = obj.favorite_data or {}
        _ensure_structure(data, class_val, chapter_val, length_str)
        ck, chk = str(class_val), str(chapter_val)
        ids = data[ck][chk][length_str]
        wid = int(word_id)
        if wid not in ids:
            ids.append(wid)
        obj.favorite_data = data
        obj.save()
        return Response({'status': 'success', 'message': 'Word added to favorites'})


class FavoritesRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        class_val = request.data.get('class')
        chapter_val = request.data.get('chapter')
        word_id = request.data.get('word_id')
        word_length = request.data.get('word_length')
        if class_val is None or chapter_val is None or word_id is None or word_length is None:
            return Response(
                {'status': 'error', 'message': 'Missing class, chapter, word_id, or word_length'},
                status=status.HTTP_400_BAD_REQUEST
            )
        class_val, chapter_val = str(class_val), str(chapter_val)
        length_str = str(word_length)
        obj = _get_or_create_favorites(request.user)
        data = obj.favorite_data or {}
        ck, chk = str(class_val), str(chapter_val)
        if ck in data and chk in data[ck] and length_str in data[ck][chk]:
            wid = int(word_id) if word_id is not None else word_id
            ids = data[ck][chk][length_str]
            if wid in ids:
                ids.remove(wid)
        obj.favorite_data = data
        obj.save()
        return Response({'status': 'success', 'message': 'Word removed from favorites'})
