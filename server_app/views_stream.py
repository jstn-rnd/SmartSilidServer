# views.py

from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from PIL import ImageGrab
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Global flag to control streaming
streaming_active = False

def generate_screen_stream(request):
    global streaming_active
    while streaming_active:
        try:
            # Capture the screen
            screen = ImageGrab.grab()
            if screen is None:
                logging.warning("Failed to capture screen.")
                continue

            # Convert to numpy array and then to OpenCV format
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Failed to encode frame.")
                continue

            # Convert the encoded frame to bytes and yield
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            logging.info("Stream ended.")


def start_stream(request):
    global streaming_active
    streaming_active = True
    logging.info("Streaming started")
    return redirect('stream_page')

def stop_stream(request):
    global streaming_active
    streaming_active = False
    logging.info("Streaming stopped")
    return redirect('stream_page')


def stream_view(request):
    global streaming_active
    if not streaming_active:
        return JsonResponse({'error': 'Streaming not active'}, status=400)
    return StreamingHttpResponse(generate_screen_stream(request),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def stream_page(request):
    return render(request, 'stream_page.html')
