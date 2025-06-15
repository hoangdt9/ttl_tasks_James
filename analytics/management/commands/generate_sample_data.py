from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics.models import Event, TicketType, Order, TicketPurchase, Organizer
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate sample data for analytics task'

    def handle(self, *args, **kwargs):
        Organizer.objects.all().delete()
        Event.objects.all().delete()
        TicketType.objects.all().delete()
        Order.objects.all().delete()
        TicketPurchase.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()  # Giữ lại superuser nếu có

        # Create organizers
        organizers = [Organizer.objects.create(name=f'Organizer {i}') for i in range(3)]
        # Create users
        users = [User.objects.create_user(username=f'user{i}', password='123') for i in range(10)]
        # Create events (with and without capacity)
        events = []
        for i in range(5):
            start = datetime.now() + timedelta(days=random.randint(1, 30))
            end = start + timedelta(hours=2)
            event = Event.objects.create(
                name=f'Event {i}',
                organizer=random.choice(organizers),
                start_time=start,
                end_time=end,
                location=f"Location {i}",
                is_published=True,
                capacity=random.choice([None, 100, 200]),
                start_date=start,
                base_ticket_price=random.randint(10, 100)
            )
            events.append(event)
        # Create ticket types for each event
        ticket_types = []
        for event in events:
            for j in range(2):
                tt = TicketType.objects.create(
                    event=event,
                    name=f'Type {j}',
                    price=random.randint(10, 100),
                    quantity_available=random.randint(10, 200),
                    is_active=True
                )
                ticket_types.append(tt)
        # Create orders (paid/unpaid, registered/anonymous)
        for _ in range(30):
            customer = random.choice([None] + users)
            is_paid = random.choice([True, False])
            order = Order.objects.create(
                customer=customer,
                is_paid=is_paid,
                total_amount=random.randint(20, 500)  # hoặc tính toán hợp lý hơn
            )
            # Create ticket purchases for each order
            for _ in range(random.randint(1, 3)):
                tt = random.choice(ticket_types)
                TicketPurchase.objects.create(
                    order=order,
                    ticket_type=tt,
                    quantity=random.randint(1, 5),
                    purchase_price_per_unit=tt.price
                )
        self.stdout.write(self.style.SUCCESS('Sample data generated.')) 