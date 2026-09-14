
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, ReservationViewSet, TableViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menu-items", MenuItemViewSet, basename="menu-item")
router.register(r"tables", TableViewSet, basename="table")
router.register(r"reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("", include(router.urls)),
]