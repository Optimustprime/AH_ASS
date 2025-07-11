from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time

from core.models import Advertiser, BudgetEvent, ClickEvent, SpendSummary



def create_or_update_spend_summary(advertiser_id, click_event_date):
    """Create or update SpendSummary for an advertiser on a given date."""
    try:
        advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)

        # Define window boundaries (start and end of day)
        window_start = datetime.combine(click_event_date.date(), time.min)
        window_end = datetime.combine(click_event_date.date(), time.max)

        # Make timezone aware
        window_start = timezone.make_aware(window_start)
        window_end = timezone.make_aware(window_end)

        # Get latest budget for this advertiser
        latest_budget = BudgetEvent.objects.filter(advertiser=advertiser).order_by('-event_time').first()

        if not latest_budget:
            return None

        budget_at_time = latest_budget.new_budget_value
        print(f"Budget at time: {budget_at_time}")

        # Calculate gross spend from click events in this window
        click_events = ClickEvent.objects.filter(
            advertiser=advertiser,
            click_time__range=(window_start, window_end),
            is_valid=True
        )

        gross_spend = click_events.aggregate(
            total=Sum('amount')
        )['total'] or 0.0

        # Calculate net spend (cannot exceed budget)
        net_spend = min(gross_spend, budget_at_time)

        # Determine if can serve (net spend hasn't reached budget)
        can_serve = net_spend < budget_at_time

        # Create or update SpendSummary
        spend_summary, created = SpendSummary.objects.update_or_create(
            advertiser=advertiser,
            window_start=window_start,
            window_end=window_end,
            defaults={
                'gross_spend': gross_spend,
                'net_spend': net_spend,
                'budget_at_time': budget_at_time,
                'can_serve': can_serve
            }
        )

        return spend_summary

    except Exception as e:
        print(f"Error creating/updating SpendSummary: {e}")
        return None