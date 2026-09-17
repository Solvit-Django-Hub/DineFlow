
import uuid
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
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
    OrderPaymentInputSerializer,
    OrderSerializer,
    PaymentSerializer,
    ReservationSerializer,
    TableSerializer,
)


@extend_schema(tags=["Analytics & Reporting"])
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def restaurant_status_view(request):

    total_tables = Table.objects.count()
    available_tables = Table.objects.filter(status=Table.Status.AVAILABLE).count()
    return Response(
        {
            "status": "OPEN",
            "server_time": timezone.now().isoformat(),
            "total_tables": total_tables,
            "available_tables": available_tables,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(tags=["Analytics & Reporting"])
class RestaurantMetricsView(APIView):


    permission_classes = [permissions.IsAuthenticated, IsStaffRole]

    def get(self, request):

        total_revenue = (
            Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(
                total=Sum("amount")
            )["total"]
            or 0.00
        )
        active_orders = Order.objects.exclude(
            status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED]
        ).count()
        total_reservations = Reservation.objects.count()

        return Response(
            {
                "total_revenue": total_revenue,
                "active_orders": active_orders,
                "total_reservations": total_reservations,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Menu Management"])
class CustomerMenuListView(generics.ListAPIView):


    queryset = MenuItem.objects.filter(is_available=True).select_related("category")
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_available"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]
    ordering = ["category", "name"]


@extend_schema(tags=["Reservations"])
class StaffReservationAuditView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):


    queryset = Reservation.objects.select_related("customer", "table").all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffRole]

    def get(self, request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        return self.create(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(tags=["Menu Management"]),
    retrieve=extend_schema(tags=["Menu Management"]),
    create=extend_schema(tags=["Menu Management"]),
    update=extend_schema(tags=["Menu Management"]),
    partial_update=extend_schema(tags=["Menu Management"]),
    destroy=extend_schema(tags=["Menu Management"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
   

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsStaffRole()]


@extend_schema_view(
    list=extend_schema(tags=["Menu Management"]),
    retrieve=extend_schema(tags=["Menu Management"]),
    create=extend_schema(tags=["Menu Management"]),
    update=extend_schema(tags=["Menu Management"]),
    partial_update=extend_schema(tags=["Menu Management"]),
    destroy=extend_schema(tags=["Menu Management"]),
)
class MenuItemViewSet(viewsets.ModelViewSet):


    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_available"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name", "created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsStaffRole()]


@extend_schema_view(
    list=extend_schema(tags=["Table Management"]),
    retrieve=extend_schema(tags=["Table Management"]),
    create=extend_schema(tags=["Table Management"]),
    update=extend_schema(tags=["Table Management"]),
    partial_update=extend_schema(tags=["Table Management"]),
    destroy=extend_schema(tags=["Table Management"]),
)
class TableViewSet(viewsets.ModelViewSet):
  

    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "location", "capacity"]
    ordering_fields = ["table_number", "capacity"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "available"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsStaffRole()]

    @action(detail=False, methods=["get"], url_path="available")
    def available(self, request):

        available_tables = self.get_queryset().filter(status=Table.Status.AVAILABLE)
        serializer = self.get_serializer(available_tables, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Reservations"]),
    retrieve=extend_schema(tags=["Reservations"]),
    create=extend_schema(tags=["Reservations"]),
    update=extend_schema(tags=["Reservations"]),
    partial_update=extend_schema(tags=["Reservations"]),
    destroy=extend_schema(tags=["Reservations"]),
)
class ReservationViewSet(viewsets.ModelViewSet):


    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "reservation_date", "table"]
    ordering_fields = ["reservation_date", "reservation_time"]

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

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsStaffRole],
        url_path="confirm",
    )
    def confirm(self, request, pk=None):

        reservation = self.get_object()
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save()
        return Response({"status": "Reservation confirmed."})

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsStaffRole],
        url_path="complete",
    )
    def complete(self, request, pk=None):

        reservation = self.get_object()
        reservation.status = Reservation.Status.COMPLETED
        reservation.save()
        return Response({"status": "Reservation completed."})


@extend_schema_view(
    list=extend_schema(tags=["Orders & Kitchen"]),
    retrieve=extend_schema(tags=["Orders & Kitchen"]),
    create=extend_schema(tags=["Orders & Kitchen"]),
    update=extend_schema(tags=["Orders & Kitchen"]),
    partial_update=extend_schema(tags=["Orders & Kitchen"]),
    destroy=extend_schema(tags=["Orders & Kitchen"]),
)
class OrderViewSet(viewsets.ModelViewSet):


    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "table"]
    ordering_fields = ["created_at", "total_amount"]

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

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsStaffRole],
        url_path="advance-status",
    )
    def advance_status(self, request, pk=None):

        order = self.get_object()
        transitions = {
            Order.Status.PENDING: Order.Status.PREPARING,
            Order.Status.PREPARING: Order.Status.SERVED,
        }
        next_status = transitions.get(order.status)
        if not next_status:
            return Response(
                {"detail": f"Cannot advance order from status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = next_status
        order.save()
        return Response({"status": order.status})

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):

        order = self.get_object()
        if order.status in [Order.Status.SERVED, Order.Status.COMPLETED]:
            return Response(
                {"detail": "Cannot cancel an order that has already been served or completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Order.Status.CANCELLED
        order.save()
        if order.table:
            order.table.status = Table.Status.AVAILABLE
            order.table.save()
        return Response({"status": "Order cancelled."})

    @extend_schema(
        request=OrderPaymentInputSerializer,
        responses={201: PaymentSerializer},
        summary="Process payment for an order",
    )
    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):

        order = self.get_object()

        if hasattr(order, "payment"):
            return Response(
                {"detail": "This order has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status == Order.Status.CANCELLED:
            return Response(
                {"detail": "Cannot pay for a cancelled order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderPaymentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_method = serializer.validated_data["payment_method"]

        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method=payment_method,
                status=Payment.Status.COMPLETED,
                transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            )
            order.status = Order.Status.COMPLETED
            order.save()

            if order.table:
                order.table.status = Table.Status.AVAILABLE
                order.table.save()

        output_serializer = PaymentSerializer(payment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["Payments & Billing"]),
    retrieve=extend_schema(tags=["Payments & Billing"]),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):


    queryset = Payment.objects.select_related("order").all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "payment_method"]
    ordering_fields = ["amount", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.STAFF, User.Role.ADMIN] or user.is_superuser:
            return Payment.objects.select_related("order").all()
        return Payment.objects.select_related("order").filter(
            order__customer=user
        )