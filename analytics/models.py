from decimal import Decimal
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models


class Organizer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        Organizer, on_delete=models.CASCADE, related_name="events"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)

    base_ticket_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return self.name


class TicketType(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="ticket_types"
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.name} - {self.name}"


class Order(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    is_paid = models.BooleanField(default=False)

    discount_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username if self.customer else 'Anonymous'}"


class TicketPurchase(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="ticket_purchases"
    )
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.PROTECT, related_name="purchases"
    )
    quantity = models.PositiveIntegerField(default=1)
    purchase_price_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Actual price paid per unit

    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name} for Order #{self.order.id}"
