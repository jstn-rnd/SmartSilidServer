import subprocess
import tempfile
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Computer
from rest_framework.decorators import api_view
from rest_framework.response import Response
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



# @api_view(['POST'])
# def start_stream(request): 
#     computer = Computer.objects.filter(is_admin = 1, status = 1).first()

#     if not computer: 
#         return Response({'status_message': 'Computer not found or computer is turned off'})
    
#     global streaming_active 
#     streaming_active = True

#     python_script_content = f'''
# import requests
# import io
# import time
# from PIL import ImageGrab, Image, ImageDraw
# import pyautogui

# SERVER_URL = 'http://192.168.10.112:8000/upload/'  # Replace with your actual server URL

# def draw_cursor_on_image(image, cursor_position):
#     cursor_radius = 10  # Adjust size as needed
#     cursor_color = (0, 0, 255)  # Blue cursor

#     cursor_overlay = Image.new("RGBA", (cursor_radius * 2, cursor_radius * 2), (0, 0, 0, 0))
#     draw = ImageDraw.Draw(cursor_overlay)
#     draw.ellipse([(0, 0), (cursor_radius * 2, cursor_radius * 2)], fill=cursor_color)

#     image.paste(cursor_overlay, (cursor_position[0] - cursor_radius, cursor_position[1] - cursor_radius), cursor_overlay)
#     return image

# def capture_screen_with_cursor():
#     screen = ImageGrab.grab()
#     cursor_position = pyautogui.position()
#     screen = draw_cursor_on_image(screen, cursor_position)
#     screen = screen.convert("RGB")
#     return screen

# def capture_and_send():
#     frame_interval = 1 / 30  # Targeting 30 FPS

#     while True:
#         start_time = time.time()
#         try:
#             img = capture_screen_with_cursor()
#             with io.BytesIO() as buffer:
#                 img.save(buffer, format="JPEG")
#                 buffer.seek(0)
#                 files = {{'file': ('screen.jpg', buffer, 'image/jpeg')}}
#                 response = requests.post(SERVER_URL, files=files)
#                 if response.status_code != 200:
#                     print(f"Failed to send frame to server: {{response.status_code}}, {{response.text}}")
#         except Exception as e:
#             print(f"An error occurred: {{e}}")

#         elapsed_time = time.time() - start_time
#         time_to_sleep = max(frame_interval - elapsed_time, 0)
#         time.sleep(time_to_sleep)

# if __name__ == "__main__":
#     try:
#         capture_and_send()
#     except KeyboardInterrupt:
#         print("Capture process interrupted by user.")
# '''
        
#     ps_script = f"""
#         $username = "Administrator"
#         $password = "Admin123"
#         $computer = "{computer.computer_name}"

#         $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
        
#         $credential = New-Object System.Management.Automation.PSCredential -ArgumentList $username, $securePassword
#         $session = New-PSSession -ComputerName $computer -Credential $credential    

#         if (Test-WSMan -ComputerName $computer) {{
#             Write-Host "Connection to $computer successful."
#         }} else {{
#             Write-Host "Connection to $computer failed."
#         }}
           
#         Invoke-Command -Session $session -ScriptBlock {{ 
#             $script = @"{python_script_content}"@
#             $tempScriptPath = [System.IO.Path]::Combine($env:TEMP, 'script.py')
#             $script | Set-Content -Path $tempScriptPath
#             $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
#             if ($pythonCommand) {{
#                 & $pythonCommand.Source $tempScriptPath
#             }} else {{
#                 Write-Host "Python is not found in the PATH."
#             }}
#          }}

#         """

#     result = subprocess.run(
#     ["powershell.exe", "-Command", ps_script],
#     capture_output=True,
#     text=True
#     )

#     return Response({
#         "status" : "Streaming successful", 
#         "Output" : result.stdout,
#         "Error:" : result.stderr
#     })



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

@api_view(["POST"])
def upload_screen(request):
    """Receive a screen capture from the client and update the frame queue."""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        frame_bytes = file.read()
        frame_queue.put(frame_bytes)  # Add frame to the queue
        return Response({'status': 'success'})
    return Response({'status': 'error'}, status=400)

def control_view(request):
    """Render the control page for the stream."""
    return render(request, 'server_app/control_stream.html')


# $pythonPath = where python | Select-Object -First 1
#             if ($pythonPath) {{
#                 & $pythonPath $tempScriptPath
#             }} else {{
#                 Write-Host "Python executable not found."
#             }}
    

    #     

    #     $session = New-PSSession -ComputerName $computer -Credential $credential
        
# $script = @"{python_script_content}"@

#         $tempScriptPath = [System.IO.Path]::GetTempFileName() + ".py"
#         $script | Set-Content -Path $tempScriptPath

#         Invoke-Command -Session $session -ScriptBlock {{ python $tempScriptPath }}