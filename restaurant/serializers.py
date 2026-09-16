
from datetime import date
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import (
    Category,
    MenuItem,
    Order,
    OrderItem,
    Payment,
    Reservation,
    Table,
)


class MenuItemSerializer(serializers.ModelSerializer):


    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "is_available",
            "created_at",
            "updated_at",
        )

    def validate_price(self, value):

        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class CategorySerializer(serializers.ModelSerializer):


    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "menu_items")


class TableSerializer(serializers.ModelSerializer):


    class Meta:
        model = Table
        fields = ("id", "table_number", "capacity", "status", "location")

    def validate_capacity(self, value):

        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1 seat.")
        return value


class ReservationSerializer(serializers.ModelSerializer):


    customer_username = serializers.ReadOnlyField(source="customer.username")
    customer_email = serializers.ReadOnlyField(source="customer.email")
    table_number = serializers.ReadOnlyField(source="table.table_number")

    class Meta:
        model = Reservation
        fields = (
            "id",
            "customer",
            "customer_username",
            "customer_email",
            "table",
            "table_number",
            "reservation_date",
            "reservation_time",
            "party_size",
            "special_requests",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "customer", "created_at", "updated_at")

    def validate_reservation_date(self, value):
        
        if value < date.today():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        return value

    def validate(self, attrs):
       
        table = attrs.get("table")
        party_size = attrs.get("party_size")
        reservation_date = attrs.get("reservation_date")
        reservation_time = attrs.get("reservation_time")

        if table and party_size and party_size > table.capacity:
            raise serializers.ValidationError(
                {
                    "party_size": (
                        f"Party size ({party_size}) exceeds Table "
                        f"{table.table_number} capacity ({table.capacity})."
                    )
                }
            )

        existing_conflict = (
            Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
            )
            .exclude(status=Reservation.Status.CANCELLED)
        )

        if self.instance:
            existing_conflict = existing_conflict.exclude(pk=self.instance.pk)

        if existing_conflict.exists():
            raise serializers.ValidationError(
                {
                    "table": (
                        f"Table {table.table_number} is already reserved for "
                        f"{reservation_date} at {reservation_time}."
                    )
                }
            )

        return attrs


class OrderItemInputSerializer(serializers.Serializer):
  

    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):


    menu_item_name = serializers.ReadOnlyField(source="menu_item.name")

    class Meta:
        model = OrderItem
        fields = ("id", "menu_item", "menu_item_name", "quantity", "unit_price")


class OrderSerializer(serializers.ModelSerializer):
 

    customer_username = serializers.ReadOnlyField(source="customer.username")
    table_number = serializers.ReadOnlyField(source="table.table_number")
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = OrderItemInputSerializer(
        many=True, write_only=True, required=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "customer_username",
            "table",
            "table_number",
            "status",
            "total_amount",
            "items",
            "order_items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "customer", "total_amount", "created_at", "updated_at")

    def validate_order_items(self, value):
        
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")

        for item_data in value:
            menu_item = item_data["menu_item"]
            if not menu_item.is_available:
                raise serializers.ValidationError(
                    f"'{menu_item.name}' is currently unavailable."
                )
        return value

    def create(self, validated_data):
        
        order_items_data = validated_data.pop("order_items")

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total = Decimal("0.00")

            for item_data in order_items_data:
                menu_item = item_data["menu_item"]
                quantity = item_data["quantity"]
                unit_price = menu_item.price

                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=unit_price,
                )
                total += unit_price * quantity

            order.total_amount = total
            order.save()

        return order


class PaymentSerializer(serializers.ModelSerializer):
   

    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order"
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "order_id",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        
        order = attrs.get("order")
        amount = attrs.get("amount")

        if order.payment is not None if hasattr(order, "payment") else False:
            raise serializers.ValidationError("This order is already paid.")

        if amount != order.total_amount:
            raise serializers.ValidationError(
                {
                    "amount": (
                        f"Payment amount (${amount}) does not match order total "
                        f"(${order.total_amount})."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        
        with transaction.atomic():
            payment = Payment.objects.create(**validated_data)
            if payment.status == Payment.Status.COMPLETED:
                payment.order.status = Order.Status.COMPLETED
                payment.order.save()
        return payment