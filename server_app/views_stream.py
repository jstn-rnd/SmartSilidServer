from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from PIL import ImageGrab
import cv2
import numpy as np
import logging
from django.views.decorators.csrf import csrf_exempt

logging.basicConfig(level=logging.DEBUG)

streaming_active = False

def stream_status(request):
    """Return the current streaming status."""
    return JsonResponse({'active': streaming_active})

def generate_screen_stream(request):
    """Generator function that yields frames for streaming."""
    global streaming_active
    try:
        while streaming_active:
            # Capture the screen
            screen = ImageGrab.grab()
            if screen is None:
                logging.warning("Failed to capture screen.")
                continue

            # Convert the screen capture to a format suitable for streaming
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR

            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Failed to encode frame.")
                continue

            # Yield the encoded frame as part of the multipart response
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Stream ended.")

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
    return StreamingHttpResponse(generate_screen_stream(request),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def control_view(request):
    """Render the control page for the stream."""
    return render(request, 'server_app/control_stream.html')
