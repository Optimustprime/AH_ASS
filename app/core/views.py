import asyncio
from typing import AsyncGenerator

from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
from django.shortcuts import render

from .helper import randomize_list, business_requirements
from .models import click_1, conversions_1, click_2, click_3, click_4, conversions_2, conversions_3, conversions_4


async def sse_stream(request, campaign_id: int) -> StreamingHttpResponse:
    """
    Sends server-sent events to the client. This function handles the streaming of banners
    for a specific campaign, updating the banners based on different business scenarios.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        StreamingHttpResponse: A streaming HTTP response with server-sent events.
    """
    # Run business requirements concurrently
    sets_of_business_scenerios = await asyncio.gather(
        sync_to_async(business_requirements)(campaign_id, click_1, conversions_1),
        sync_to_async(business_requirements)(campaign_id, click_2, conversions_2),
        sync_to_async(business_requirements)(campaign_id, click_3, conversions_3),
        sync_to_async(business_requirements)(campaign_id, click_4, conversions_4)
    )

    async def event_stream() -> AsyncGenerator[str, None]:
        """
       Generates the server-sent events by iterating through business scenarios,
       randomizing the banner order, and yielding the banners one by one.

       Yields:
           str: The next banner data to be sent to the client.
       """
        try:
            while True:
                for scenerio in sets_of_business_scenerios:
                    scenerio = randomize_list(scenerio)
                    duration = round((15 * 60) / len(scenerio), 1)
                    for items in scenerio:
                        yield f'data: {items}\n\n'
                        await asyncio.sleep(duration)
        finally:
            return

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'close'
    return response


def index(request):
    """
    Renders the banner HTML page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page.
    """
    return render(request, 'banner.html')
