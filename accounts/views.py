from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .permissions import IsAdminRole
from .serializers import (
    AdminUserSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserProfileSerializer,
    VerifyEmailSerializer,
    generate_and_send_verification_code,
)


@extend_schema(tags=["Authentication & Users"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@extend_schema(tags=["Authentication & Users"])
class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        user.is_email_verified = True
        user.verification_code = None
        user.verification_code_expires_at = None
        user.save(update_fields=["is_email_verified", "verification_code", "verification_code_expires_at"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "detail": "Email verified successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "is_email_verified": user.is_email_verified,
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Authentication & Users"])
class ResendVerificationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.get(email=email)
        generate_and_send_verification_code(user)

        return Response(
            {"detail": "A new 6-digit verification code has been sent to your email."},
            status=status.HTTP_200_OK,
        )


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
    create=extend_schema(tags=["Authentication & Users"], summary="Create user (Admin only)"),
    retrieve=extend_schema(tags=["Authentication & Users"], summary="Retrieve user details"),
    update=extend_schema(tags=["Authentication & Users"], summary="Update user (Admin only)"),
    partial_update=extend_schema(tags=["Authentication & Users"], summary="Partial update user"),
    destroy=extend_schema(tags=["Authentication & Users"], summary="Delete user (Admin only)"),
)
class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ["role", "is_active", "is_email_verified"]
    search_fields = ["username", "email", "phone_number", "first_name", "last_name"]