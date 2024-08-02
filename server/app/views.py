from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action


from app.serializers import LoginSerializer, UserSerializer

from drf_spectacular.utils import extend_schema
# Create your views here.




class AppViewSet(viewsets.GenericViewSet):
    
    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.login(
            request,
            serializer.validated_data["phone"],  # type: ignore
            serializer.validated_data["password"],  # type: ignore
            serializer.validated_data["fcm_token"] # type: ignore
        )
        return Response(status=status.HTTP_200_OK, data=result["data"], headers=result["token"])