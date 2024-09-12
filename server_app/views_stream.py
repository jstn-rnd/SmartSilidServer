from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import queue

# Global state
streaming_active = False
frame_queue = queue.Queue(maxsize = 500)  # No max size limit

def stream_status(request):
    """Return the current streaming status."""
    return JsonResponse({'active': streaming_active})

def generate_screen_stream():
    """Generator function that yields frames for MJPEG streaming."""
    while streaming_active:
        try:
            frame_bytes = frame_queue.get(timeout=1)  # Wait for a frame
            if frame_bytes:
                # Send the frame and immediately release it from the queue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                frame_queue.task_done()  # Mark this frame as processed
        except queue.Empty:
            continue

@csrf_exempt
def start_stream(request):
    """Start streaming."""
    global streaming_active
    streaming_active = True
    return HttpResponse("Streaming started.")

@csrf_exempt
def stop_stream(request):
    """Stop streaming."""
    global streaming_active
    streaming_active = False
    return HttpResponse("Streaming stopped.")

def stream_view(request):
    """View to stream the screen capture."""
    if not streaming_active:
        return HttpResponse("Streaming is not active.")
    return StreamingHttpResponse(generate_screen_stream(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def upload_screen(request):
    """Receive a screen capture from the client and update the frame queue."""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        frame_bytes = file.read()
        frame_queue.put(frame_bytes)  # Add frame to the queue
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def control_view(request):
    """Render the control page for the stream."""
    return render(request, 'server_app/control_stream.html')
