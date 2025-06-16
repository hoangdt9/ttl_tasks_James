# Event Analytics System

**worked by James. ttl_task_James**

A Django-based analytics system for event management and ticket sales tracking.

## Project Overview

This project implements a set of analytics functions to track and analyze event data, ticket sales, and customer purchase patterns. The system is built using Django and focuses on efficient database queries and comprehensive data analysis.

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install django
```

3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Run tests:

```bash
python manage.py test analytics
```

## Project Structure

- `analytics/models.py`: Contains the data models for Events, TicketTypes, Orders, and TicketPurchases
- `analytics/event_analytics.py`: Implements the core analytics functions
- `analytics/tests.py`: Contains unit tests for the analytics functions

## Analytics Functions

### 1. get_upcoming_events_summary()

Returns a list of event summaries for published and ongoing/future events.

**Edge Cases Handled:**

- Events with/without capacity
- Events with no ticket sales
- Events with no ticket types
- Null values in calculations

**Optimizations:**

- Uses `prefetch_related` to minimize database queries
- Efficient aggregation using `Sum` and `Coalesce`
- Proper handling of decimal calculations

**Example Usage:**

```python
events = get_upcoming_events_summary()
# Returns: [
#     {
#         'event_id': 1,
#         'event_name': 'Concert',
#         'total_tickets_sold': 100,
#         'total_revenue': 1000.00,
#         'tickets_remaining': 50,
#         'organizer_name': 'John Doe'
#     },
#     ...
# ]
```

### 2. get_top_selling_ticket_types(num_types=5)

Returns the top selling ticket types ordered by units sold.

**Edge Cases Handled:**

- Ticket types with zero sales
- Events with no ticket types
- Paid vs unpaid orders

**Optimizations:**

- Uses `annotate` for efficient aggregation
- `select_related` to minimize queries
- Proper filtering of paid orders

**Example Usage:**

```python
top_tickets = get_top_selling_ticket_types(5)
# Returns: [
#     {
#         'id': 1,
#         'name': 'VIP Ticket',
#         'units_sold': 50,
#         'event_name': 'Concert'
#     },
#     ...
# ]
```

### 3. get_customer_purchase_statistics(customer_id)

Returns detailed purchase statistics for a specific customer.

**Edge Cases Handled:**

- Customers with no orders
- Unpaid orders
- Multiple purchases across events

**Optimizations:**

- Efficient aggregation using `annotate`
- Proper handling of decimal calculations
- Subquery optimization for most purchased event

**Example Usage:**

```python
stats = get_customer_purchase_statistics(1)
# Returns: {
#     'total_orders_placed': 5,
#     'total_amount_spent': 500.00,
#     'most_purchased_event_name': 'Concert'
# }
```

### 4. get_events_with_low_capacity_remaining(threshold_percentage=10)

Returns events that are close to reaching their capacity.

**Edge Cases Handled:**

- Events without defined capacity
- Events with no sales
- Percentage calculations

**Optimizations:**

- Efficient annotation of percentage calculations
- Proper filtering of events with capacity
- Decimal precision handling

**Example Usage:**

```python
low_capacity_events = get_events_with_low_capacity_remaining(10)
# Returns: [
#     {
#         'id': 1,
#         'name': 'Concert',
#         'percentage_tickets_remaining': 5.0
#     },
#     ...
# ]
```

## Performance Considerations

1. **Query Optimization:**

   - Used `select_related` and `prefetch_related` to minimize database hits
   - Implemented efficient aggregation using Django's ORM
   - Proper indexing on frequently queried fields

2. **Data Type Handling:**

   - Careful handling of decimal calculations
   - Proper use of `Coalesce` for null value handling
   - Consistent data type usage across calculations

3. **Edge Case Handling:**
   - Comprehensive null checks
   - Proper handling of zero values
   - Validation of input parameters

## Future Improvements

1. **Caching:**

   - Implement Redis caching for frequently accessed data
   - Cache expensive calculations
   - Implement cache invalidation strategies

2. **Performance Monitoring:**

   - Add query logging
   - Implement performance metrics
   - Monitor database query execution times

3. **Additional Features:**
   - Add date range filtering
   - Implement more detailed analytics
   - Add export functionality for reports

## Testing

The project includes comprehensive unit tests covering:

- Edge cases
- Data type handling
- Calculation accuracy
- Query optimization

Run tests using:

```bash
python manage.py test analytics
```
