from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/badminton/(?P<match_id>\d+)/$', consumers.BadmintonConsumer.as_asgi()),
    re_path(r'ws/volleyball/(?P<match_id>\d+)/$', consumers.VolleyballConsumer.as_asgi()),
    re_path(r'ws/tabletennis/(?P<match_id>\d+)/$', consumers.TableTennisConsumer.as_asgi()),
    re_path(r'ws/throwball/(?P<match_id>\d+)/$', consumers.ThrowballConsumer.as_asgi()),
    re_path(r'ws/kabaddi/(?P<match_id>\d+)/$', consumers.KabaddiConsumer.as_asgi()),
]