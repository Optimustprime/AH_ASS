from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time

from core.models import Advertiser, BudgetEvent, ClickEvent, SpendSummary
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now


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

        # Check if SpendSummary already exists for this day
        spend_summary = SpendSummary.objects.filter(
            advertiser=advertiser,
            window_start=window_start,
            window_end=window_end
        ).first()

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

        if spend_summary:
            # Update existing SpendSummary
            spend_summary.gross_spend = gross_spend
            spend_summary.net_spend = net_spend
            spend_summary.budget_at_time = budget_at_time
            spend_summary.can_serve = can_serve
            spend_summary.save()
        else:
            # Create new SpendSummary for this day
            spend_summary = SpendSummary.objects.create(
                advertiser=advertiser,
                window_start=window_start,
                window_end=window_end,
                gross_spend=gross_spend,
                net_spend=net_spend,
                budget_at_time=budget_at_time,
                can_serve=can_serve
            )


        return spend_summary

    except Exception as e:
        print(f"Error creating/updating SpendSummary: {e}")
        return None


@csrf_exempt
def update_budget(request):
    """Update advertiser budget and check against gross spend."""
    if request.method == "POST":
        try:
            data = request.POST
            advertiser_id = data.get("advertiser_id")
            new_budget_value = float(data.get("new_budget_value"))

            advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)

            # Create a new BudgetEvent
            BudgetEvent.objects.create(
                advertiser=advertiser,
                new_budget_value=new_budget_value,
                event_time=now(),
                source="UI Update"
            )

            # Update SpendSummary
            current_time = now()
            spend_summary = create_or_update_spend_summary(advertiser_id, current_time)

            if spend_summary:
                return JsonResponse({"status": "success", "message": "Budget updated successfully."})
            else:
                return JsonResponse({"status": "error", "message": "Failed to update spend summary."}, status=500)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)
