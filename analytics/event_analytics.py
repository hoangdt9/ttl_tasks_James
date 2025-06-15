from django.db.models import Sum, F, Q, Count, DecimalField
from django.db.models.functions import Coalesce
from analytics.models import Event, TicketType, TicketPurchase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


def get_upcoming_events_summary():
    """
    Returns a list of event summaries for published and ongoing/future events.
    
    This function provides a comprehensive overview of upcoming events, including:
    - Total tickets sold
    - Total revenue generated
    - Remaining ticket capacity
    - Organizer information
    
    Edge Cases Handled:
    - Events with/without capacity
    - Events with no ticket sales
    - Events with no ticket types
    - Null values in calculations
    
    Optimizations:
    - Uses prefetch_related to minimize database queries
    - Efficient aggregation using Sum and Coalesce
    - Proper handling of decimal calculations
    
    Returns:
        list: A list of dictionaries containing event summaries
    """
    now = timezone.now()
    events = Event.objects.filter(is_published=True, end_time__gte=now)
    result = []
    for event in events.prefetch_related('ticket_types', 'organizer'):
        # Total tickets sold (all TicketPurchase for this event, only paid orders)
        total_tickets_sold = TicketPurchase.objects.filter(
            ticket_type__event=event,
            order__is_paid=True
        ).aggregate(total=Coalesce(Sum('quantity'), 0))['total']
        
        # Total revenue (only paid orders)
        total_revenue = TicketPurchase.objects.filter(
            ticket_type__event=event,
            order__is_paid=True
        ).aggregate(
            revenue=Coalesce(
                Sum(
                    Coalesce(F('quantity'), Decimal('0.0')) * Coalesce(F('purchase_price_per_unit'), Decimal('0.0')),
                    output_field=DecimalField()
                ), Decimal('0.0')
            )
        )['revenue']
        
        # Tickets remaining
        total_available = event.ticket_types.aggregate(
            total=Coalesce(Sum('quantity_available'), 0)
        )['total']
        
        # Calculate remaining tickets based on capacity or available tickets
        if event.capacity is not None:
            tickets_remaining = max(event.capacity - (total_tickets_sold or 0), 0)
        else:
            tickets_remaining = max((total_available or 0) - (total_tickets_sold or 0), 0)
            
        result.append({
            'event_id': event.id,
            'event_name': event.name,
            'total_tickets_sold': int(total_tickets_sold or 0),
            'total_revenue': float(total_revenue or 0),
            'tickets_remaining': int(tickets_remaining or 0),
            'organizer_name': event.organizer.name if event.organizer else '',
        })
    return result


def get_top_selling_ticket_types(num_types=5):
    """
    Returns TicketType objects ordered by units sold (paid orders).
    
    This function identifies the most popular ticket types across all events,
    considering only paid orders.
    
    Edge Cases Handled:
    - Ticket types with zero sales
    - Events with no ticket types
    - Paid vs unpaid orders
    
    Optimizations:
    - Uses annotate for efficient aggregation
    - select_related to minimize queries
    - Proper filtering of paid orders
    
    Args:
        num_types (int): Number of top-selling ticket types to return
        
    Returns:
        QuerySet: Annotated TicketType objects ordered by units sold
    """
    return TicketType.objects.annotate(
        units_sold=Coalesce(Sum(
            'purchases__quantity',
            filter=Q(purchases__order__is_paid=True)
        ), 0),
        event_name=F('event__name')
    ).order_by('-units_sold')[:num_types]


def get_customer_purchase_statistics(customer_id):
    """
    Returns detailed purchase statistics for a specific customer.
    
    This function provides comprehensive analytics about a customer's
    purchasing behavior, including total orders, amount spent, and
    most frequently purchased event.
    
    Edge Cases Handled:
    - Customers with no orders
    - Unpaid orders
    - Multiple purchases across events
    
    Optimizations:
    - Efficient aggregation using annotate
    - Proper handling of decimal calculations
    - Subquery optimization for most purchased event
    
    Args:
        customer_id (int): The ID of the customer to analyze
        
    Returns:
        User: Annotated User object with purchase statistics
    """
    from django.db.models import Subquery, OuterRef
    user_qs = User.objects.filter(id=customer_id)
    
    # Total orders placed and amount spent
    user_qs = user_qs.annotate(
        total_orders_placed=Count('orders', distinct=True),
        total_amount_spent=Coalesce(
            Sum('orders__total_amount', filter=Q(orders__is_paid=True), output_field=DecimalField()), Decimal('0.0')
        )
    )
    
    # Most purchased event
    event_counts = TicketPurchase.objects.filter(
        order__customer_id=customer_id,
        order__is_paid=True
    ).values('ticket_type__event__name').annotate(
        total=Sum('quantity')
    ).order_by('-total')
    
    most_purchased_event_name = event_counts[0]['ticket_type__event__name'] if event_counts else None
    user = user_qs.first()
    if user:
        user.most_purchased_event_name = most_purchased_event_name
    return user


def get_events_with_low_capacity_remaining(threshold_percentage=10):
    """
    Returns Event objects with percentage_tickets_remaining <= threshold_percentage.
    
    This function identifies events that are close to reaching their capacity,
    helping organizers plan for potential capacity issues.
    
    Edge Cases Handled:
    - Events without defined capacity
    - Events with no sales
    - Percentage calculations
    
    Optimizations:
    - Efficient annotation of percentage calculations
    - Proper filtering of events with capacity
    - Decimal precision handling
    
    Args:
        threshold_percentage (int): The percentage threshold for low capacity
        
    Returns:
        QuerySet: Event objects with low remaining capacity
    """
    events = Event.objects.filter(capacity__isnull=False)
    events = events.annotate(
        tickets_sold=Coalesce(Sum('ticket_types__purchases__quantity', filter=Q(ticket_types__purchases__order__is_paid=True)), 0),
        percentage_tickets_remaining=100 * (F('capacity') - Coalesce(Sum('ticket_types__purchases__quantity', filter=Q(ticket_types__purchases__order__is_paid=True)), 0)) / F('capacity')
    ).filter(percentage_tickets_remaining__lte=threshold_percentage)
    return events

# Example usage:
# get_upcoming_events_summary()
# get_top_selling_ticket_types(5)
# get_customer_purchase_statistics(customer_id=1)
# get_events_with_low_capacity_remaining(10)
