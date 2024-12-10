import random
import string
import queue
from io import BytesIO
from PIL import Image
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Global state
streaming_active = False
stream_token = ""
frame_queue = queue.Queue(maxsize=500)  # Frame queue for MJPEG streaming
stream_token = None  # Token for the active stream

def generate_token():
    """Generate a 6-letter uppercase token for the stream."""
    return ''.join(random.choices(string.ascii_uppercase, k=6))

@api_view(["GET"])
def streaming_status(request):
    """
    Endpoint for clients to check if streaming is active.
    """
    global streaming_active
    return JsonResponse({
        'streaming_active': streaming_active,
        'token' : stream_token,
        })

def clear_queue(q):
    """
    Helper function to clear all items in the queue.
    """
    while not q.empty():
        try:
            q.get_nowait()
            q.task_done()
        except queue.Empty:
            break

def generate_screen_stream():
    """
    Generator function that yields frames for MJPEG streaming.
    Clears the queue before starting to send frames.
    """
    # Clear any old frames
    clear_queue(frame_queue)

    while streaming_active:
        try:
            frame_bytes = frame_queue.get(timeout=0.1)  # Wait for a frame
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                frame_queue.task_done()  # Mark this frame as processed
        except queue.Empty:
            continue

@csrf_exempt
def start_stream(request):
    """
    Start streaming and generate a token.
    Clear any old frames from the queue.
    """
    global streaming_active, stream_token

    # Prevent starting a new stream if one is already active
    if streaming_active:
        return JsonResponse({'message': 'Streaming is already active.', 'token': stream_token}, status=400)

    streaming_active = True
    stream_token = generate_token()  # Generate a new token for the session
    clear_queue(frame_queue)  # Clear any old frames

    return JsonResponse({
        'message': 'Streaming started.',
        'token': stream_token  # Return the generated token
    })

@csrf_exempt
def stop_stream(request):
    """Stop streaming and invalidate the token."""
    global streaming_active, stream_token

    if not streaming_active:
        return JsonResponse({'message': 'No active stream to stop.'}, status=400)

    streaming_active = False
    stream_token = None  # Invalidate the token
    return JsonResponse({'message': 'Streaming stopped.'})

def stream_view(request):
    """
    View to stream the screen capture with token validation.
    """
    global stream_token

    entered_token = request.GET.get('token', '')  # Get the token from the URL

    if entered_token == '':
        # If no token is entered, show the form
        return render(request, 'server_app/stream.html', {'token_error': False})

    # If token is valid, stream the content
    if entered_token == stream_token:
        # Clear queue before starting the stream
        return StreamingHttpResponse(generate_screen_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

    # If token is invalid, show the form with an error message
    return render(request, 'server_app/stream.html', {'token_error': True})

@api_view(["POST"])
def upload_screen(request):
    """
    Receive a screen capture from the client and update the frame queue.
    """
    global streaming_active

    if not streaming_active:
        return Response({'status': 'error', 'message': 'Streaming is not active.'}, status=403)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        frame_bytes = compress_image(file.read())  # Compress before adding
        frame_queue.put(frame_bytes)  # Add frame to the queue
        return Response({'status': 'success'})
    return Response({'status': 'error'}, status=400)
    
def compress_image(image):
    """Compress the image before adding it to the frame queue."""
    img = Image.open(BytesIO(image))
    img = img.convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=50)  # Compress with 50% quality
    return buffer.getvalue()

def control_view(request):
    """Render the control page for the stream."""
    global streaming_active, stream_token
    context = {'streaming_active': streaming_active, 'stream_token': stream_token}
    return render(request, 'server_app/control_stream.html', context)