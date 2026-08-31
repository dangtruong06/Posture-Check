from rest_framework.routers import DefaultRouter
from .views import PostureSummaryViewSet, google_login
from django.urls import path

router = DefaultRouter()
router.register(r'posture_summaries', PostureSummaryViewSet, basename='posture_summaries')

urlpatterns = router.urls + [
    path('auth/google/', google_login),
]