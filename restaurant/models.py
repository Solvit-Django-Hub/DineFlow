
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
   

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class MenuItem(models.Model):
  

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="menu_items"
    )
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Table(models.Model):
    

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"

    class Location(models.TextChoices):
        INDOOR = "INDOOR", "Indoor"
        OUTDOOR = "OUTDOOR", "Outdoor"
        ROOFTOP = "ROOFTOP", "Rooftop"
        BALCONY = "BALCONY", "Balcony"

    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    location = models.CharField(
        max_length=10,
        choices=Location.choices,
        default=Location.INDOOR,
    )

    objects = models.Manager()

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats - {self.status})"


class Reservation(models.Model):
    """Reservation model representing table bookings."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    party_size = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ["-reservation_date", "-reservation_time"]

    def __str__(self):
        return (
            f"Reservation #{self.pk} on {self.reservation_date} "
            f"at {self.reservation_time}"
        )