from django.http import StreamingHttpResponse
import cv2

def generate_stream():
    cap = cv2.VideoCapture('http://192.168.10.119:8000')  # Capture from the VidStream output
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def stream_view(request):
    return StreamingHttpResponse(generate_stream(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')