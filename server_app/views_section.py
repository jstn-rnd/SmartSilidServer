from .models import Section
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .configurations import AD_BASE_DN
import pyad
from .settings import get_ad_connection
from .serializers import SectionSerializer
import win32com.client
import pythoncom

#Case na invalid sa db pero okay sa ad
#User authentication sa api, kelangan admin
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_section(request): 
    
    section_name = request.data.get("name")
    
    section_object = Section.objects.filter(name = section_name).first()
    
    if section_object : 
        return Response({
            "status_message" : "Section already exists"
        })
    
    else : 
        try :
            pythoncom.CoInitialize()
            parent_dn = f"OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            ad = win32com.client.Dispatch("ADsNameSpaces")
            ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
            ou = ad_obj.Create("organizationalUnit", f"OU={section_name}")
            ou.SetInfo()
            
            new_section = SectionSerializer(data=request.data)
            if new_section.is_valid(): 
                new_section.save()
                return Response({
                    "status_message" : f"Section {section_name} has been added succesfully"
                })
            
            else: 
                  
                try:
                    ou.DeleteObject(0)

                except Exception as delete_error:
                    # Handle exception if OU deletion fails
                    return Response({
                        "status_message": f"Section {section_name} has not been added, but failed to clean up AD entry.",
                        "error_message": str(delete_error)
                    })
                
                return Response({
                    "status_message": f"Section {section_name} has not been added",
                    "error_message": "Invalid section data"
                })

        except Exception as e : 
            return Response({
                "status_message" : "Failed to create section",
                "error_message" : str(e)
            })
         

#delete section 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_section(request):
    section_name = request.data.get("name")

    if not section_name: 
        return Response({
            "status_message" : "Missing or invalid input"
        })

    section_object = Section.objects.filter(name=section_name).first()

    if section_object : 
        try : 
            pythoncom.CoInitialize()
            parent_dn = f"OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            ad = win32com.client.Dispatch("ADsNameSpaces")
            ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
            ou = ad_obj.Create("organizationalUnit", f"OU={section_name}") # HIndi dito nag ccreate, niloload lang ganun
            ou.DeleteObject(0)

            section_object.delete()

            return Response({
                "status_message" : f"Section {section_name} has been deleted successfully"
            })
        
        except Exception as e : 
            return Response({
                "status_message" : "Failed to delete section",
                "error_message" : str(e)
            })
    
    else : 
        return Response({
            "status_message" : f"Section {section_name} does not exist"
        })
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_sections(request):
    sections = Section.objects.all()
    response_json = []

    for section in sections: 
        name = section.name
        response_json.append({"name" : name}) 

    return Response({
        "status_message" : "Request Succesful",
        "sections" : response_json
    })    

#get all section 

#get one section

