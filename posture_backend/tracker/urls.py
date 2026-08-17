from rest_framework.routers import DefaultRouter
from .views import PostureSummaryViewSet

router = DefaultRouter()
router.register(r'posture_summaries', PostureSummaryViewSet)

urlpatterns = router.urls