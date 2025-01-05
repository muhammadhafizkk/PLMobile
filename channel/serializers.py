from rest_framework import serializers

class ChannelSerializer(serializers.Serializer):
    _id = serializers.CharField()  # MongoDB Object ID as a string
    channel_name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(max_length=255, required=False)
    privacy = serializers.CharField(max_length=50, required=False)
    sensor = serializers.ListField(child=serializers.DictField(), required=False)  # Array of sensors
    allow_API = serializers.CharField(max_length=50, required=False)  # Field to allow or restrict API access
    API_KEY = serializers.CharField(max_length=255, required=False)  # API key
    user_id = serializers.CharField(max_length=50, required=False)  # User ID as a string
    date_created = serializers.CharField(allow_blank=True, required=False)  # Date as a string
    date_modified = serializers.CharField(allow_blank=True, required=False)  # Date as a string  # To handle the array of sensors
