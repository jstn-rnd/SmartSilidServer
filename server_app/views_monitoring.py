from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
import hashlib
import logging

# In-memory store for screen captures
screen_captures = {}

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@csrf_exempt
def upload_screen(request):
    """Handle file upload for screen captures."""
    if request.method == 'POST' and 'file' in request.FILES:
        client_id = request.POST.get('client_id', 'default_client')
        image = request.FILES['file']
        try:
            screen_captures[client_id] = image.read()
            logging.info(f"Screen capture uploaded for client_id: {client_id}")
            return HttpResponse("Screen capture uploaded.", status=200)
        except Exception as e:
            logging.error(f"Failed to upload screen capture: {e}")
            return HttpResponse("Failed to upload screen capture.", status=500)
    return HttpResponse("Invalid request.", status=400)

def view_screen(request, client_id):
    """Serve the screen capture for a specific client with optimization and caching."""
    if client_id in screen_captures:
        screen_image = screen_captures[client_id]
        
        # Open and preprocess the image
        image = Image.open(io.BytesIO(screen_image))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", optimize=True, quality=75)  # Adjust quality as needed
        optimized_image = buffer.getvalue()
        
        # Create a unique ETag based on the content hash
        etag = hashlib.md5(optimized_image).hexdigest()
        
        response = HttpResponse(optimized_image, content_type='image/jpeg')
        response['ETag'] = etag
        response['Cache-Control'] = 'public, max-age=1'  # Cache for 1 second
        
        # Handle If-None-Match header for efficient caching
        if request.headers.get('If-None-Match') == etag:
            response.status_code = 304
            response.content = b''
        
        return response
    
    logging.warning(f"No screen capture available for client_id: {client_id}")
    return HttpResponse("No screen capture available for this client.", status=404)

def client_screens_view(request):
    """Render the client screens page."""
    return render(request, 'server_app/client_screens.html')
