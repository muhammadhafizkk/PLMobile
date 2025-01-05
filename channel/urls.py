from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),
    path('channels/', views.ChannelList.as_view(), name='channel-list'),
    path('channels/create/', views.create_channel, name='create-channel'),
    path('channels/<str:channel_id>/edit', views.update_channel, name='update_channel'),
    path('channels/delete/<str:channel_id>', views.delete_channel, name='delete_channel'),
    path('channels/stats/', views.get_channel_statistics, name='channel_statistics'),
]