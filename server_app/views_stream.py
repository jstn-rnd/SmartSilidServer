# server_app/views.py

from django.http import JsonResponse
from django.views import View
from django.conf import settings
from vidstream import StreamingServer

class StartStreamingView(View):
    def get(self, request, *args, **kwargs):
        host = '192.168.10.119'  # Bind to all network interfaces
        port = 8000  # Or any other available port
        self.server = StreamingServer(host, port)
        self.server.start_server()
        streaming_url = f"http://{settings.SITE_HOST}:{port}/stream/"
        return JsonResponse({'streaming_url': streaming_url})

class StopStreamingView(View):
    def get(self, request, *args, **kwargs):
        if hasattr(self, 'server'):
            self.server.stop_server()
        return JsonResponse({'status': 'stopped'})
