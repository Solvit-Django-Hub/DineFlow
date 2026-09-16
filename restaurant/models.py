
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


class Order(models.Model):


    class Status(models.TextChoices):


        PENDING = "PENDING", "Pending"
        PREPARING = "PREPARING", "Preparing"
        SERVED = "SERVED", "Served"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:


        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer} - ${self.total_amount}"


class OrderItem(models.Model):


    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    objects = models.Manager()

    class Meta:
 

        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (${self.unit_price})"


class Payment(models.Model):


    class Method(models.TextChoices):

        CASH = "CASH", "Cash"
        CARD = "CARD", "Credit/Debit Card"
        ONLINE = "ONLINE", "Online"

    class Status(models.TextChoices):


        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=10,
        choices=Method.choices,
        default=Method.CARD,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:


        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.pk} - ${self.amount} ({self.status})"