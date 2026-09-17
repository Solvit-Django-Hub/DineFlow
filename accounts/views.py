from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .permissions import IsAdminRole
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)


@extend_schema(tags=["Authentication & Users"])
class RegisterView(generics.CreateAPIView):


    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@extend_schema(tags=["Authentication & Users"])
class CustomTokenObtainPairView(TokenObtainPairView):


    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=["Authentication & Users"])
class ProfileView(generics.RetrieveUpdateAPIView):


    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Authentication & Users"])
class ChangePasswordView(APIView):


    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(tags=["Authentication & Users"], summary="List users (Admin only)"),
    retrieve=extend_schema(tags=["Authentication & Users"], summary="Retrieve user details"),
    partial_update=extend_schema(tags=["Authentication & Users"], summary="Update user role/status"),
)
class UserManagementViewSet(viewsets.ModelViewSet):


    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "phone_number"]