from rest_framework import viewsets
from .models import PostureSummary
from .serializers import PostureSummarySerializer

# Create your views here.
class PostureSummaryViewSet(viewsets.ModelViewSet):
    queryset = PostureSummary.objects.all()
    serializer_class = PostureSummarySerializer