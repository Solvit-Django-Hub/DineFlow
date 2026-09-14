from django.contrib import admin
from .models import Category, MenuItem, Reservation, Table


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "created_at")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "capacity", "status", "location")
    list_filter = ("status", "location")
    search_fields = ("table_number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "table",
        "reservation_date",
        "reservation_time",
        "party_size",
        "status",
    )
    list_filter = ("status", "reservation_date")
    search_fields = ("customer__username", "customer__email", "table__table_number")