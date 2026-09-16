
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from accounts.models import User
from accounts.permissions import IsStaffRole
from .models import (
    Category,
    MenuItem,
    Order,
    Payment,
    Reservation,
    Table,
)
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    ReservationSerializer,
    TableSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):


    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsStaffRole()]


class MenuItemViewSet(viewsets.ModelViewSet):


    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsStaffRole()]


class TableViewSet(viewsets.ModelViewSet):
 

    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsStaffRole()]


class ReservationViewSet(viewsets.ModelViewSet):


    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.STAFF, User.Role.ADMIN] or user.is_superuser:
            return Reservation.objects.select_related("customer", "table").all()
        return Reservation.objects.select_related("customer", "table").filter(
            customer=user
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = Reservation.Status.CANCELLED
        instance.save()
        return Response(
            {"detail": "Reservation has been cancelled."},
            status=status.HTTP_200_OK,
        )


class OrderViewSet(viewsets.ModelViewSet):


    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.STAFF, User.Role.ADMIN] or user.is_superuser:
            return (
                Order.objects.select_related("customer", "table")
                .prefetch_related("items__menu_item")
                .all()
            )
        return (
            Order.objects.select_related("customer", "table")
            .prefetch_related("items__menu_item")
            .filter(customer=user)
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):


    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.STAFF, User.Role.ADMIN] or user.is_superuser:
            return Payment.objects.select_related("order").all()
        return Payment.objects.select_related("order").filter(
            order__customer=user
        )