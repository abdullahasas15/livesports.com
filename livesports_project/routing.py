from django.urls import re_path
from apps.scores.consumers import BadmintonConsumer

websocket_urlpatterns = [
    re_path(r'ws/badminton/(?P<match_id>\w+)/$', BadmintonConsumer.as_asgi()),
]