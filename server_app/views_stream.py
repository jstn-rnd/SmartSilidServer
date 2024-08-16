# views.py
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
    return JsonResponse({'active': streaming_active})

def generate_screen_stream(request):
    global streaming_active
    try:
        while streaming_active:
            
            screen = ImageGrab.grab()
            if screen is None:
                logging.warning("Failed to capture screen.")
                continue

           
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR

          
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Failed to encode frame.")
                continue

          
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Stream ended.")

@csrf_exempt
def start_stream(request):
    global streaming_active
    streaming_active = True
    return HttpResponse("Streaming started.")

@csrf_exempt
def stop_stream(request):
    global streaming_active
    streaming_active = False
    return HttpResponse("Streaming stopped.")

def stream_view(request):
    if not streaming_active:
        return HttpResponse("Streaming is not active.")
    return StreamingHttpResponse(generate_screen_stream(request),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def control_view(request):
    return render(request, 'server_app/control_stream.html')
