from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Computer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Computer)
def computer_status_changed(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    message = {
        'id': instance.id,
        'name': instance.computer_name,
        'status': instance.status
    }
    print("*************************************************************")
    
    # Send the message to the WebSocket group
    async_to_sync(channel_layer.group_send)(
        'computer_status_updates',
        {
            'type': 'send_status_update',
            'message': message
        }
    )