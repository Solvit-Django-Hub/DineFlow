from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    CustomerMenuListView,
    MenuItemViewSet,
    OrderViewSet,
    PaymentViewSet,
    ReservationViewSet,
    RestaurantMetricsView,
    StaffReservationAuditView,
    TableViewSet,
    restaurant_status_view,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menu-items", MenuItemViewSet, basename="menu-item")
router.register(r"tables", TableViewSet, basename="table")
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("status/", restaurant_status_view, name="restaurant_status"),
    path("metrics/", RestaurantMetricsView.as_view(), name="restaurant_metrics"),
    path("menu-catalog/", CustomerMenuListView.as_view(), name="customer_menu_catalog"),
    path(
        "staff-reservations/",
        StaffReservationAuditView.as_view(),
        name="staff_reservation_audit",
    ),
    path("", include(router.urls)),
]