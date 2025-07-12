from random import choice
from .models import User, Advertiser, Ad, ClickEvent, BudgetEvent, SpendSummary
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
from core.serializers import UserSerializer, AdvertiserSerializer
from core.utils import create_or_update_spend_summary
from django.utils import timezone
import time


class CreateUserView(generics.CreateAPIView):
    """Create a new user and associated advertiser in the system."""
    serializer_class = UserSerializer
    permission_classes = [HasAPIKey]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create advertiser first if advertiser data is provided
        advertiser_data = request.data.get('advertiser')
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
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class ManageUserView(viewsets.ViewSetMixin, generics.RetrieveUpdateAPIView):
    """Manage the authenticated user and edit data."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):
        return self.request.user


async def get_valid_ads(advertiser_id: int) -> list:
    """Get valid ads for an advertiser based on budget and spend."""
    advertiser = await sync_to_async(Advertiser.objects.get)(advertiser_id=advertiser_id)

    budget_query = BudgetEvent.objects.filter(advertiser=advertiser).order_by('-event_time')

    # Execute query and print all results

    latest_budget = await sync_to_async(
        lambda: budget_query.first()
    )()

    # Get current spend
    current_spend = await sync_to_async(
        lambda: SpendSummary.objects.filter(advertiser=advertiser).order_by('-window_end').first()
    )()

    if not latest_budget or not current_spend or not current_spend.can_serve:
        return []

    # Get valid ads
    ads = await sync_to_async(
        lambda: list(Ad.objects.filter(
            advertiser=advertiser,
            is_active=True
        ).values('ad_id', 'ad_title', 'ad_format', 'product_link'))
    )()

    return ads

async def sse_stream(request, advertiser_id: int) -> StreamingHttpResponse:
    """Stream valid ads for an advertiser, one at a time."""
    # Get valid ads asynchronously first (like your working example)
    advertiser = await sync_to_async(Advertiser.objects.get)(advertiser_id=advertiser_id)
    spend_summary = await sync_to_async(
        lambda: SpendSummary.objects.filter(advertiser=advertiser).order_by('-window_end').first()
    )()

    if not spend_summary or not spend_summary.can_serve:
        def empty_stream():
            yield f'data: {json.dumps({"message": "Cannot serve ads due to budget constraints"})}\n\n'
        response = StreamingHttpResponse(empty_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'close'
        return response

    valid_ads = await get_valid_ads(advertiser_id)

    def event_stream():  # Remove async here
        """Generate server-sent events, sending one ad at a time."""

        try:
            while True:
                if valid_ads:
                    for ad in valid_ads:
                        current_ad = ad
                        yield f'data: {json.dumps(current_ad)}\n\n'
                        time.sleep(5)  # Synchronous sleep instead of await asyncio.sleep(5)

                    time.sleep(10)  # Synchronous sleep instead of await asyncio.sleep(10)

        except Exception as e:
            print(f"Stream error: {e}")
            yield f'data: {json.dumps({"message": "Error in stream"})}\n\n'
        finally:
            return

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'close'
    return response



def serve_ads(request, advertiser_id):
    """Render the ad serving page."""
    return render(request, 'ads.html', {'advertiser_id': advertiser_id})



@csrf_exempt
@require_http_methods(["POST"])
def track_ad_click(request):
    """Track ad click and send to Kafka."""
    try:
        data = json.loads(request.body)
        advertiser_id = data.get('advertiser_id')
        ad_id = data.get('ad_id')

        if not advertiser_id or not ad_id:
            return HttpResponse(
                json.dumps({"error": "Missing advertiser_id or ad_id"}),
                content_type="application/json",
                status=400
            )
        # Assign a random amount
        random_amount = choice([1.0, 1.1, 1.2, 1.3, 1.4])


        # Create a ClickEvent instance
        advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)

        # Retrieve the latest budget value for the advertiser
        latest_budget = BudgetEvent.objects.filter(advertiser=advertiser).order_by('-event_time').first()
        latest_budget_value = latest_budget.new_budget_value if latest_budget else 0.0
        click_time = timezone.now()

        ad = Ad.objects.get(ad_id=ad_id)
        ClickEvent.objects.create(
            advertiser=advertiser,
            ad=ad,
            amount=random_amount,
            click_time=click_time
        )

        # Create or update SpendSummary after click event
        create_or_update_spend_summary(advertiser_id, click_time)

        producer = AzureKafkaClickProducer()
        success = producer.send_click_event(
            advertiser=advertiser.name,
            advertiser_id=advertiser_id,
            ad_id=ad_id,
            amount=random_amount,
            budget_value=latest_budget_value
        )
        producer.close()

        if success:
            return HttpResponse(
                json.dumps({"status": "success"}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"error": "Failed to send event"}),
                content_type="application/json",
                status=500
            )

    except Exception as e:
        print(f"Error tracking click: {e}")
        return HttpResponse(
            json.dumps({"error": "Internal server error"}),
            content_type="application/json",
            status=500
        )

def advertiser_budget_update(request):
    """Render the advertiser budget update page."""
    return render(request, 'advertiser_budget_update.html')