from django.urls import path
from . import views

# Define a list of url patterns
urlpatterns = [
    # CONTROL SENSOR API PERMISSIONS
    path('<str:channel_id>/permit_API', views.permit_API, name="permit_API"),
    path('<str:channel_id>/forbid_API', views.forbid_API, name="forbid_API"),

    # RETRIEVE DASHBOARD DATA
    path('<str:channel_id>/get_dashboard_data/', views.getDashboardData, name="getDashboardData"),

    # VIEW PUBLIC DASHBOARD OR EMBED
    path('<str:channel_id>/get_shared_dashboard', views.getSharedDashboardDetail, name="getSharedDashboardDetail"),
    
    # SHARE DASHBOARD , CHART , AND TABLE
    path('<str:channel_id>/shared_dashboard/', views.sharedDashboard, name="sharedDashboard"),
    path('embed/channel/<str:channel_id>/', views.render_embed_code, name='render_embed_code'),
    path('<str:channel_id>/share_chart/phChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_ph_chart, name="share_ph_chart"),
    path('<str:channel_id>/share_chart/humidityChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_humidity_chart, name="share_humidity_chart"),
    path('<str:channel_id>/share_chart/temperatureChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_temperature_chart, name="share_temperature_chart"),
    path('<str:channel_id>/share_chart/rainfallChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_rainfall_chart, name="share_rainfall_chart"),
    path('<str:channel_id>/share_chart/nitrogenChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_nitrogen_chart, name="share_nitrogen_chart"),
    path('<str:channel_id>/share_chart/potassiumChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_potassium_chart, name="share_potassium_chart"),
    path('<str:channel_id>/share_chart/phosphorousChart/<str:start_date>/<str:end_date>/<str:chart_name>/', views.share_phosphorous_chart, name="share_phosphorous_chart"),
    path('<str:channel_id>/share_table/cropTable/<str:start_date>/<str:end_date>/<str:table_name>/', views.share_crop_table, name="share_crop_table"),
    
    # RENDER CHART BASED ON TIMEFRAME
    path('ph_data/<str:channel_id>/<str:start_date>/<str:end_date>/', views.getPHData, name='get_ph_data'),
    path('humidity_temperature/<str:channel_id>/<str:start_date>/<str:end_date>/', views.getHumidityTemperatureData, name='getHumidityTemperatureData'),
    path('NPK/<str:channel_id>/<str:start_date>/<str:end_date>/', views.getNPKData, name='getNPKData'),
    path('rainfall_data/<str:channel_id>/<str:start_date>/<str:end_date>/', views.getRainfallData, name='getRainfallData'),
    #path('<str:channel_id>/getCropRecommendationByDate/<str:start_date>/<str:end_date>/', views.getCropRecommendationByDate, name='getCropRecommendationByDate'),

    path('<str:channel_id>/manage_sensor', views.manage_sensor, name="manage_sensor"),

    path('<str:channel_id>/edit_sensor/<str:sensor_type>/<str:sensor_id>/', views.edit_sensor, name="edit_sensor"),
    path('<str:channel_id>/add_sensor', views.add_sensor, name="add_sensor"),
    path('<str:channel_id>/delete_sensor/<str:sensor_type>/', views.delete_sensor, name="delete_sensor"),
]