from django.urls import path

from .views import room_views, topic_views, user_views, message_views, profile_views

urlpatterns = [
    path('rooms/', room_views.rooms, name='rooms'),
    path('rooms/<int:pk>/', room_views.room_detail, name='room-detail'),
    path("rooms/<int:pk>/messages", room_views.room_messages, name="room-messages"),
    path('users/', user_views.users, name='api-users'),
    path('users/<int:pk>/', user_views.user_detail, name='api-user'), 
    path('messages/<int:pk>/', message_views.message_detail, name='api-message'),
    path('topics/<int:pk>/', topic_views.topic_detail, name="topic-detail"),
    path('topics/', topic_views.topic_create, name="topic-create"),
    path("profiles/me/", profile_views.me_profile, name="me-profile"),
    path("profiles/<int:user_id>/", profile_views.public_profile, name="public-profile"),
]