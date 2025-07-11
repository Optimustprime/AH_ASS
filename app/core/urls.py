from django.urls import path
from core import views
from core.utils import update_budget

# app_name = 'core'

urlpatterns = [
    path('users/create/', views.CreateUserView.as_view(), name='create-user'),
    path('users/me/', views.ManageUserView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='manage-user'),
    path('ads/stream/<int:advertiser_id>/', views.sse_stream, name='ad-stream'),
    path('ads/serve/<int:advertiser_id>/', views.serve_ads, name='serve-ads'),
    path('ads/track-click/', views.track_ad_click, name='track_ad_click'),
    path('update-budget/', update_budget, name='update-budget'),
]

from django.core.asgi import get_asgi_application
application = get_asgi_application()