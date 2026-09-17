from datetime import date, timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Category, MenuItem, Order, Table


class RestaurantAPITests(APITestCase):


    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff_member",
            email="staff@dineflow.com",
            password="Password123!",
            role=User.Role.STAFF,
        )
        self.customer_user = User.objects.create_user(
            username="customer_tester",
            email="customer@dineflow.com",
            password="Password123!",
            role=User.Role.CUSTOMER,
        )

        self.category = Category.objects.create(
            name="Entrees", description="Main course meals"
        )
        self.dish = MenuItem.objects.create(
            category=self.category,
            name="Grilled Salmon",
            price=Decimal("18.50"),
            is_available=True,
        )
        self.table = Table.objects.create(
            table_number=15,
            capacity=4,
            status=Table.Status.AVAILABLE,
            location=Table.Location.INDOOR,
        )

    def test_public_can_view_menu(self):

        url = reverse("menu-item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_create_menu_item(self):

        self.client.force_authenticate(user=self.customer_user)
        url = reverse("menu-item-list")
        data = {
            "category": self.category.id,
            "name": "Unauthorized Pasta",
            "price": "12.00",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reservation_capacity_validation(self):

        self.client.force_authenticate(user=self.customer_user)
        url = reverse("reservation-list")
        tomorrow = date.today() + timedelta(days=1)
        data = {
            "table": self.table.id,
            "reservation_date": tomorrow.isoformat(),
            "reservation_time": "19:00:00",
            "party_size": 8,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_creation_and_payment_flow(self):

        self.client.force_authenticate(user=self.customer_user)

        order_url = reverse("order-list")
        order_data = {
            "table": self.table.id,
            "order_items": [
                {"menu_item": self.dish.id, "quantity": 2}
            ],
        }
        order_response = self.client.post(order_url, order_data, format="json")
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(order_response.data["total_amount"]), Decimal("37.00"))

        order_id = order_response.data["id"]

        pay_url = reverse("order-pay", kwargs={"pk": order_id})
        pay_data = {"payment_method": "CARD"}
        pay_response = self.client.post(pay_url, pay_data)
        self.assertEqual(pay_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pay_response.data["status"], "COMPLETED")

        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.status, Order.Status.COMPLETED)