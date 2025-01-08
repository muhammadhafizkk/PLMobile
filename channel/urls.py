from django.urls import path
from channel import views as views

urlpatterns = [
    path('', views.ChannelList.as_view(), name='channel-list'),
    path('create/', views.create_channel, name='create-channel'),
    path('<str:channel_id>/edit', views.update_channel, name='update_channel'),
    path('delete/<str:channel_id>', views.delete_channel, name='delete_channel'),
    path('stats/', views.get_channel_statistics, name='channel_statistics'),

    # RETRIEVE DASHBOARD DATA
    path('<str:channel_id>/get_dashboard_data/', views.getDashboardData, name="getDashboardData"),

    path('<str:channel_id>/share_chart/<str:chart_type>/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_chart, name="share_chart"),
]