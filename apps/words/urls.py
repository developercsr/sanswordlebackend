"""
Words URL configuration.
"""
from django.urls import path
from .views import (
    WordListCreateView,
    WordsByClassChapterView,
    MyWordsView,
    WordDetailView,
    WordDetailsByWordView,
    WordVerifyView,
    ExcelTemplateDownloadView,
    ExcelUploadView,
    WordUploadView,
    WordTemplateView,
    BulkUploadView,
)

urlpatterns = [
    path('', WordListCreateView.as_view(), name='word-list-create'),
    path('template/', WordTemplateView.as_view(), name='word-template'),
    path('upload/', WordUploadView.as_view(), name='word-upload'),
    path('bulk-upload/', BulkUploadView.as_view(), name='word-bulk-upload'),
    path('by-class-chapter/', WordsByClassChapterView.as_view(), name='words-by-class-chapter'),
    path('details/', WordDetailsByWordView.as_view(), name='word-details-by-word'),
    path('my-words/', MyWordsView.as_view(), name='words-my-words'),
    path('excel-template/download/', ExcelTemplateDownloadView.as_view(), name='word-excel-download'),
    path('excel-upload/', ExcelUploadView.as_view(), name='word-excel-upload'),
    path('<int:pk>/', WordDetailView.as_view(), name='word-detail'),
    path('<int:pk>/verify/', WordVerifyView.as_view(), name='word-verify'),
]
