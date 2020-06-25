from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import BlockRequestDetailView, BlockRequestListView

urlpatterns = [
    path('block_request/', BlockRequestListView.as_view(), name='block_request_list'),
    path('block_request/<int:pk>/', BlockRequestDetailView.as_view(), name='block_request_detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
