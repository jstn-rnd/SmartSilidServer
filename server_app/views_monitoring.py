from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import queue
from .models import Computer

# Global state for handling frames for each client
frame_queues = {}

def generate_monitor_stream(client_id):
    """Generator function that yields MJPEG frames."""
    while client_id in frame_queues:
        frame_queue = frame_queues[client_id]
        try:
            frame_bytes = frame_queue.get(timeout=10)  # Timeout after 10 seconds of no frame
            if frame_bytes:
                # Return the frame as part of the MJPEG stream
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                frame_queue.task_done()  # Mark the frame as processed
        except queue.Empty:
            continue

def monitor_stream_view(request, client_id):
    """View to stream the screen captures for a specific client."""
    # Ensure that the client exists in the Computer model
    computer = get_object_or_404(Computer, computer_name=client_id)
    return StreamingHttpResponse(generate_monitor_stream(client_id),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def upload_monitor_screen(request):
    """Receive a screen capture from the client and update the frame queue."""
    if request.method == 'POST' and request.FILES.get('file'):
        client_id = request.POST.get('client_id')
        file = request.FILES['file']
        frame_bytes = file.read()

        # Initialize the queue for this client if not already initialized
        if client_id not in frame_queues:
            frame_queues[client_id] = queue.Queue(maxsize=500)

        # Add the frame to the client's queue
        try:
            frame_queues[client_id].put_nowait(frame_bytes)
            return JsonResponse({'status': 'success'})
        except queue.Full:
            # If the queue is full, return an error
            return JsonResponse({'status': 'error', 'message': 'Queue is full.'}, status=503)
    
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def start_stream(request):
    """Start streaming for a particular client."""
    # This endpoint could be used to initialize the streaming, if needed
    return HttpResponse("Streaming started.")

@csrf_exempt
def stop_stream(request):
    """Stop streaming for a particular client."""
    # You can stop streaming by clearing the queue or disconnecting the client
    client_id = request.POST.get('client_id')
    if client_id in frame_queues:
        del frame_queues[client_id]  # Remove the client queue from the server
        return HttpResponse("Streaming stopped.")
    return JsonResponse({'status': 'error', 'message': 'Client not found.'}, status=404)

def client_screens_view(request):
    """Render the control page for monitoring all connected clients."""
    computers = Computer.objects.all()  # Assuming you have a Computer model
    return render(request, 'server_app/client_screens.html', {'computers': computers})