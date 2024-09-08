from .models import Section
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .configurations import AD_BASE_DN
import pyad
from .settings import get_ad_connection
from .serializers import SectionSerializer

#Case na invalid sa db pero okay sa ad
@api_view(['POST'])
def add_section(request): 
    
    section_name = request.data.get("section_name")
    
    section_object = Section.objects.filter(name = section_name).first()
    
    if section_object : 
        return Response({
            "status_message" : "Section already exists"
        })
    
    else : 
        try :
            if get_ad_connection() : 
                
                container = pyad.adcontainer.ADContainer.from_dn(f"OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}")
                ad_section = pyad.adcontainer.ADContainer.create(section_name, container)
                print("**********************************")
                if ad_section : 
                    section_name = SectionSerializer(data=request.data)
                    if section_name.is_valid(): 
                        section_name.save()
                    
                        return Response({
                            "status_message" : "Section added succesfully"
                        })
            
            else : 
                return Response({
                        "status_message" : "Cannot connect to the active directory"
                    })

        except Exception as e : 
            return Response({
                "status_message" : "Failed to create section",
                "error_message" : str(e)
            })
        

#delete section 

#get all section 

#get one section