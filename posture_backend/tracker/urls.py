from rest_framework.routers import DefaultRouter
from .views import PostureSummaryViewSet, google_login
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

router = DefaultRouter()
router.register(r'posture_summaries', PostureSummaryViewSet, basename='posture_summaries')

urlpatterns = router.urls + [
    path('auth/google/', google_login),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]