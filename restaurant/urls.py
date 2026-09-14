from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, TableViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menu-items", MenuItemViewSet, basename="menu-item")
router.register(r"tables", TableViewSet, basename="table")

urlpatterns = [
    path("", include(router.urls)),
]