from django.urls import path
from channel import views as views
from dashboard import views as views2

urlpatterns = [
    path('', views.ChannelList.as_view(), name='channel-list'),
    path('create/', views.create_channel, name='create-channel'),
    path('<str:channel_id>/edit', views.update_channel, name='update_channel'),
    path('delete/<str:channel_id>', views.delete_channel, name='delete_channel'),
    path('stats/', views.get_channel_statistics, name='channel_statistics'),
]