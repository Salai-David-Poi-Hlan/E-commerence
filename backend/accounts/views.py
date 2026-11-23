from rest_framework import generics,permissions
from rest_framework.throttling import ScopedRateThrottle
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]
    authentication_classes=[]
    throttle_classes=[ScopedRateThrottle]
    throttle_scope='register'



class MeView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):
        u=request.user
        return Response({'username':u.username,'email':u.email,'is_staff':u.is_staff})