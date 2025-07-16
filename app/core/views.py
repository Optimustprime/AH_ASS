from random import choice
from .models import Advertiser, Ad, ClickEvent, SpendSummary
from rest_framework import authentication, generics, status, viewsets
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .azure_kafka_producer import AzureKafkaClickProducer
import json
from .serializers import UserSerializer, AdvertiserSerializer
from .utils import create_or_update_spend_summary, BudgetManager
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)


class CreateUserView(generics.CreateAPIView):
    """Create a new user and associated advertiser in the system."""

    serializer_class = UserSerializer
    permission_classes = [HasAPIKey]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create advertiser first if advertiser data is provided
        advertiser_data = request.data.get("advertiser")
        advertiser = None
        if advertiser_data:
            advertiser_serializer = AdvertiserSerializer(data=advertiser_data)
            advertiser_serializer.is_valid(raise_exception=True)
            advertiser = advertiser_serializer.save()

        # Create user and link to advertiser
        user = serializer.save()
        if advertiser:
            user.advertiser = advertiser
            user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ManageUserView(viewsets.ViewSetMixin, generics.RetrieveUpdateAPIView):
    """Manage the authenticated user and edit data."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):
        return self.request.user


async def get_valid_ads(advertiser_id: int) -> list:
    """Get valid ads for an advertiser based on budget and spend."""
    try:
        advertiser = await sync_to_async(Advertiser.objects.get)(
            advertiser_id=advertiser_id
        )

        # Use BudgetManager to get latest budget
        latest_budget = await sync_to_async(BudgetManager.get_latest_budget)(advertiser)

        # Get current spend summary
        current_spend = await sync_to_async(
            lambda: SpendSummary.objects.filter(advertiser=advertiser)
            .order_by("-window_end")
            .first()
        )()

        if not latest_budget or not current_spend or not current_spend.can_serve:
            logger.info(
                f"Cannot serve ads for advertiser {advertiser_id}: budget={bool(latest_budget)}, spend={bool(current_spend)}, can_serve={current_spend.can_serve if current_spend else False}"
            )
            return []

        # Get valid ads
        ads = await sync_to_async(
            lambda: list(
                Ad.objects.filter(advertiser=advertiser, is_active=True).values(
                    "ad_id", "ad_title", "ad_format", "product_link"
                )
            )
        )()

        return ads

    except Advertiser.DoesNotExist:
        logger.error(f"Advertiser {advertiser_id} not found")
        return []
    except Exception as e:
        logger.error(f"Error getting valid ads for advertiser {advertiser_id}: {e}")
        return []


async def sse_stream(request, advertiser_id: int) -> StreamingHttpResponse:
    """Stream valid ads for an advertiser, one at a time."""
    try:
        # Get valid ads asynchronously
        advertiser = await sync_to_async(Advertiser.objects.get)(
            advertiser_id=advertiser_id
        )
        spend_summary = await sync_to_async(
            lambda: SpendSummary.objects.filter(advertiser=advertiser)
            .order_by("-window_end")
            .first()
        )()

        if not spend_summary or not spend_summary.can_serve:

            def empty_stream():
                yield f"data: {json.dumps({'message': 'Cannot serve ads due to budget constraints'})}\n\n"

            response = StreamingHttpResponse(
                empty_stream(), content_type="text/event-stream"
            )
            response["Cache-Control"] = "no-cache"
            response["Connection"] = "close"
            return response

        valid_ads = await get_valid_ads(advertiser_id)

        def event_stream():
            """Generate server-sent events, sending one ad at a time."""
            try:
                while True:
                    if valid_ads:
                        for ad in valid_ads:
                            yield f"data: {json.dumps(ad)}\n\n"
                            time.sleep(5)
                        time.sleep(10)
                    else:
                        yield f"data: {json.dumps({'message': 'No valid ads available'})}\n\n"
                        time.sleep(10)

            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'message': 'Error in stream'})}\n\n"

        response = StreamingHttpResponse(
            event_stream(), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        response["Connection"] = "close"
        return response

    except Advertiser.DoesNotExist:
        logger.error(f"Advertiser {advertiser_id} not found")

        def error_stream():
            yield f"data: {json.dumps({'message': 'Advertiser not found'})}\n\n"

        response = StreamingHttpResponse(
            error_stream(), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        response["Connection"] = "close"
        return response


def serve_ads(request, advertiser_id):
    """Render the ad serving page."""
    return render(request, "ads.html", {"advertiser_id": advertiser_id})


@csrf_exempt
@require_http_methods(["POST"])
def track_ad_click(request):
    """Track ad click and send to Kafka."""
    try:
        data = json.loads(request.body)
        advertiser_id = data.get("advertiser_id")
        ad_id = data.get("ad_id")

        # Input validation
        if not advertiser_id or not ad_id:
            return HttpResponse(
                json.dumps({"error": "Missing advertiser_id or ad_id"}),
                content_type="application/json",
                status=400,
            )

        # Validate advertiser exists
        try:
            advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)
        except Advertiser.DoesNotExist:
            return HttpResponse(
                json.dumps({"error": "Advertiser not found"}),
                content_type="application/json",
                status=404,
            )

        # Validate ad exists
        try:
            ad = Ad.objects.get(ad_id=ad_id)
        except Ad.DoesNotExist:
            return HttpResponse(
                json.dumps({"error": "Ad not found"}),
                content_type="application/json",
                status=404,
            )

        # Assign a random amount
        random_amount = choice([1.0, 1.1, 1.2, 1.3, 1.4])
        click_time = timezone.now()

        # Get latest budget using BudgetManager
        latest_budget = BudgetManager.get_latest_budget(advertiser)
        latest_budget_value = latest_budget.new_budget_value if latest_budget else 0.0

        # Create click event
        click_event = ClickEvent.objects.create(
            advertiser=advertiser, ad=ad, amount=random_amount, click_time=click_time
        )

        # Create or update SpendSummary after click event
        spend_summary = create_or_update_spend_summary(advertiser_id, click_time)

        # Send to Kafka
        producer = AzureKafkaClickProducer()
        success = producer.send_click_event(
            advertiser=advertiser.name,
            advertiser_id=advertiser_id,
            ad_id=ad_id,
            amount=random_amount,
            budget_value=latest_budget_value,
        )
        producer.close()

        if success:
            logger.info(
                f"Click event tracked successfully for advertiser {advertiser_id}, ad {ad_id}"
            )
            return HttpResponse(
                json.dumps(
                    {
                        "status": "success",
                        "click_id": str(click_event.click_id)
                        if hasattr(click_event, "click_id")
                        else None,
                        "can_serve": spend_summary.can_serve if spend_summary else True,
                    }
                ),
                content_type="application/json",
            )
        else:
            logger.error(
                f"Failed to send click event to Kafka for advertiser {advertiser_id}"
            )
            return HttpResponse(
                json.dumps({"error": "Failed to send event to Kafka"}),
                content_type="application/json",
                status=500,
            )

    except json.JSONDecodeError:
        return HttpResponse(
            json.dumps({"error": "Invalid JSON data"}),
            content_type="application/json",
            status=400,
        )
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return HttpResponse(
            json.dumps({"error": "Internal server error"}),
            content_type="application/json",
            status=500,
        )


def advertiser_budget_update(request):
    """Render the advertiser budget update page."""
    return render(request, "advertiser_budget_update.html")
