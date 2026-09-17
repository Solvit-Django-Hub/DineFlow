
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    ProfileView,
    RegisterView,
    UserManagementViewSet,
)

router = DefaultRouter()
router.register(r"users", UserManagementViewSet, basename="user-management")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="auth_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="auth_change_password"),
    path("", include(router.urls)),
]