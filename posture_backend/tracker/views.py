from rest_framework import viewsets
from .models import PostureSummary
from .serializers import PostureSummarySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.models import User
from django.conf import settings

# Create your views here.
class PostureSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = PostureSummarySerializer
    def get_queryset(self):
        return PostureSummary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# google log in view function
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    id_token_str = request.data.get('id_token')

    if not id_token_str:
        return Response({'error': '...'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        id_info = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        return Response({'error': '...'}, status=status.HTTP_401_UNAUTHORIZED)
    
    email = id_info.get('email')

    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email':email}
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })