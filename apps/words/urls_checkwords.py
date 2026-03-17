"""Check words API URLs."""
from django.urls import path
from .views import (
    CheckWordsRandomView,
    CheckWordsApproveView,
    CheckWordsUpdateApproveView,
    CheckWordsRejectView,
    CheckWordsRemoveView,
    CheckWordsMyActionsView,
)

urlpatterns = [
    path('random/', CheckWordsRandomView.as_view(), name='checkwords-random'),
    path('approve/', CheckWordsApproveView.as_view(), name='checkwords-approve'),
    path('update-approve/', CheckWordsUpdateApproveView.as_view(), name='checkwords-update-approve'),
    path('reject/', CheckWordsRejectView.as_view(), name='checkwords-reject'),
    path('remove/', CheckWordsRemoveView.as_view(), name='checkwords-remove'),
    path('my-actions/', CheckWordsMyActionsView.as_view(), name='checkwords-my-actions'),
]
