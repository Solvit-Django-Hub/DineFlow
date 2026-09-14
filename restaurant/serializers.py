

from datetime import date
from rest_framework import serializers
from .models import Category, MenuItem, Reservation, Table


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
        """Validate that price is greater than zero."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category objects including nested items."""

    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "menu_items")


class TableSerializer(serializers.ModelSerializer):
 

    class Meta:
        model = Table
        fields = ("id", "table_number", "capacity", "status", "location")

    def validate_capacity(self, value):
        """Validate that table capacity is at least 1 seat."""
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