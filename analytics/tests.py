from django.test import TestCase
from django.contrib.auth.models import User
from analytics.event_analytics import (
    get_upcoming_events_summary,
    get_top_selling_ticket_types,
    get_customer_purchase_statistics,
    get_events_with_low_capacity_remaining
)

class AnalyticsFunctionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # You can call your data generator here if needed
        from django.core.management import call_command
        call_command('generate_sample_data')

    def test_get_upcoming_events_summary(self):
        result = get_upcoming_events_summary()
        self.assertIsInstance(result, list)
        if result:
            self.assertIn('event_id', result[0])
            self.assertIn('total_tickets_sold', result[0])

    def test_get_top_selling_ticket_types(self):
        result = get_top_selling_ticket_types(3)
        self.assertTrue(hasattr(result, '__iter__'))
        for tt in result:
            self.assertTrue(hasattr(tt, 'units_sold'))
            self.assertTrue(hasattr(tt, 'event_name'))

    def test_get_customer_purchase_statistics(self):
        user = User.objects.first()
        if user:
            stats = get_customer_purchase_statistics(user.id)
            self.assertTrue(hasattr(stats, 'total_orders_placed'))
            self.assertTrue(hasattr(stats, 'total_amount_spent'))
            self.assertTrue(hasattr(stats, 'most_purchased_event_name'))

    def test_get_events_with_low_capacity_remaining(self):
        result = get_events_with_low_capacity_remaining(50)
        self.assertTrue(hasattr(result, '__iter__'))
        for event in result:
            self.assertTrue(hasattr(event, 'percentage_tickets_remaining'))

# How to run tests:
# In your terminal, activate your virtual environment and run:
# python manage.py test analytics
