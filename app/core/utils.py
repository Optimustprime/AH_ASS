from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time
from core.models import Advertiser, BudgetEvent, ClickEvent, SpendSummary
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
import logging
from typing import Optional, Tuple
logger = logging.getLogger(__name__)


class BudgetManager:
    """Handles budget-related operations for advertisers."""

    @staticmethod
    def get_latest_budget(advertiser: Advertiser) -> Optional[BudgetEvent]:
        """Get the most recent budget event for an advertiser."""
        return BudgetEvent.objects.filter(
            advertiser=advertiser
        ).order_by('-event_time').first()

    @staticmethod
    def calculate_daily_spend(advertiser: Advertiser, window_start: datetime, window_end: datetime) -> float:
        """Calculate total spend for an advertiser within a time window."""
        click_events = ClickEvent.objects.filter(
            advertiser=advertiser,
            click_time__range=(window_start, window_end),
            is_valid=True
        )

        return click_events.aggregate(
            total=Sum('amount')
        )['total'] or 0.0

    @staticmethod
    def get_daily_window(date: datetime) -> Tuple[datetime, datetime]:
        """Get the start and end of day for a given date."""
        window_start = datetime.combine(date.date(), time.min)
        window_end = datetime.combine(date.date(), time.max)

        return (
            timezone.make_aware(window_start),
            timezone.make_aware(window_end)
        )

    @staticmethod
    def can_serve_ads(net_spend: float, budget: float) -> bool:
        """Determine if ads can be served based on spend and budget."""
        return net_spend < budget

    @staticmethod
    def calculate_net_spend(gross_spend: float, budget: float) -> float:
        """Calculate net spend ensuring it doesn't exceed budget."""
        return min(gross_spend, budget)


class SpendSummaryManager:
    """Manages spend summary operations."""

    def __init__(self):
        self.budget_manager = BudgetManager()

    def get_or_create_spend_summary(
        self,
        advertiser: Advertiser,
        window_start: datetime,
        window_end: datetime
    ) -> Optional[SpendSummary]:
        """Get existing spend summary or create new one."""
        return SpendSummary.objects.filter(
            advertiser=advertiser,
            window_start=window_start,
            window_end=window_end
        ).first()

    def update_spend_summary(
        self,
        advertiser_id: int,
        click_event_date: datetime
    ) -> Optional[SpendSummary]:
        """Create or update SpendSummary for an advertiser on a given date."""
        try:
            advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)

            # Get daily window boundaries
            window_start, window_end = self.budget_manager.get_daily_window(click_event_date)

            # Get latest budget
            latest_budget = self.budget_manager.get_latest_budget(advertiser)
            if not latest_budget:
                logger.warning(f"No budget found for advertiser {advertiser_id}")
                return None

            budget_value = latest_budget.new_budget_value

            # Calculate spend metrics
            gross_spend = self.budget_manager.calculate_daily_spend(
                advertiser, window_start, window_end
            )
            net_spend = self.budget_manager.calculate_net_spend(gross_spend, budget_value)
            can_serve = self.budget_manager.can_serve_ads(net_spend, budget_value)

            # Get or create spend summary
            spend_summary = self.get_or_create_spend_summary(
                advertiser, window_start, window_end
            )

            if spend_summary:
                # Update existing record
                spend_summary.gross_spend = gross_spend
                spend_summary.net_spend = net_spend
                spend_summary.budget_at_time = budget_value
                spend_summary.can_serve = can_serve
                spend_summary.save()
                logger.info(f"Updated spend summary for advertiser {advertiser_id}")
            else:
                # Create new record
                spend_summary = SpendSummary.objects.create(
                    advertiser=advertiser,
                    window_start=window_start,
                    window_end=window_end,
                    gross_spend=gross_spend,
                    net_spend=net_spend,
                    budget_at_time=budget_value,
                    can_serve=can_serve
                )
                logger.info(f"Created new spend summary for advertiser {advertiser_id}")

            return spend_summary

        except Advertiser.DoesNotExist:
            logger.error(f"Advertiser {advertiser_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error updating spend summary for advertiser {advertiser_id}: {e}")
            return None


class BudgetUpdateHandler:
    """Handles budget update operations."""

    def __init__(self):
        self.spend_manager = SpendSummaryManager()

    def update_advertiser_budget(
        self,
        advertiser_id: int,
        new_budget_value: float,
        source: str = "API Update"
    ) -> dict:
        """Update advertiser budget and refresh spend summary."""
        try:
            advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)

            # Validate budget value
            if new_budget_value < 0:
                return {
                    "status": "error",
                    "message": "Budget value cannot be negative"
                }

            # Create budget event
            budget_event = BudgetEvent.objects.create(
                advertiser=advertiser,
                new_budget_value=new_budget_value,
                event_time=now(),
                source=source
            )

            # Update spend summary with new budget
            spend_summary = self.spend_manager.update_spend_summary(
                advertiser_id, now()
            )

            if spend_summary:
                logger.info(f"Budget updated for advertiser {advertiser_id}: {new_budget_value}")
                return {
                    "status": "success",
                    "message": "Budget updated successfully",
                    "budget_event_id": budget_event.id,
                    "can_serve": spend_summary.can_serve,
                    "current_spend": spend_summary.net_spend
                }
            else:
                logger.warning(f"Budget updated but spend summary update failed for advertiser {advertiser_id}")
                return {
                    "status": "partial_success",
                    "message": "Budget updated but spend summary refresh failed"
                }

        except Advertiser.DoesNotExist:
            logger.error(f"Advertiser {advertiser_id} not found")
            return {
                "status": "error",
                "message": "Advertiser not found"
            }
        except Exception as e:
            logger.error(f"Error updating budget for advertiser {advertiser_id}: {e}")
            return {
                "status": "error",
                "message": f"Internal error: {str(e)}"
            }


# Public API functions
def create_or_update_spend_summary(advertiser_id: int, click_event_date: datetime) -> Optional[SpendSummary]:
    """Public API to create or update spend summary."""
    manager = SpendSummaryManager()
    return manager.update_spend_summary(advertiser_id, click_event_date)


@csrf_exempt
def update_budget(request):
    """API endpoint to update advertiser budget."""
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST method allowed"
        }, status=405)

    try:
        data = request.POST
        advertiser_id = data.get("advertiser_id")
        new_budget_value = data.get("new_budget_value")

        # Validate input
        if not advertiser_id:
            return JsonResponse({
                "status": "error",
                "message": "advertiser_id is required"
            }, status=400)

        if not new_budget_value:
            return JsonResponse({
                "status": "error",
                "message": "new_budget_value is required"
            }, status=400)

        try:
            advertiser_id = int(advertiser_id)
            new_budget_value = float(new_budget_value)
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid data types for advertiser_id or new_budget_value"
            }, status=400)

        # Update budget
        handler = BudgetUpdateHandler()
        result = handler.update_advertiser_budget(
            advertiser_id, new_budget_value, "UI Update"
        )

        status_code = 200 if result["status"] == "success" else 400
        return JsonResponse(result, status=status_code)

    except Exception as e:
        logger.error(f"Unexpected error in update_budget: {e}")
        return JsonResponse({
            "status": "error",
            "message": "Internal server error"
        }, status=500)