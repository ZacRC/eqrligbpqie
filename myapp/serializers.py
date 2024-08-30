from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id')

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'sender_id', 'message', 'is_read', 'created_at']