import datetime
import pytz
import win32com.client
from .models import Blacklist

def convert_time(time): 
    timestamp_ms = int(time[6:-2])
    timestamp_s = timestamp_ms // 1000
    dt_utc = datetime.datetime.fromtimestamp(timestamp_s)
    utc_plus_8 = pytz.timezone('Asia/Manila')  
    dt_utc8 = dt_utc.astimezone(utc_plus_8)
    return dt_utc8.strftime('%Y-%m-%d %H:%M:%S')

import win32com.client
from .models import Blacklist

import win32com.client
import pythoncom
from .models import Blacklist
import logging
from django.conf import settings
from .models import Blacklist

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import pythoncom
import win32com.client
from .models import Blacklist
from .models import Whitelist, Blacklist
from django.core.exceptions import ObjectDoesNotExist

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import traceback



# Configure logging


import win32com.client
from win32com.client import Dispatch
import pythoncom



def initialize_com():
    """Initialize COM library for the current thread."""
    pythoncom.CoInitialize()

def get_gpo(gpo_guid):
    """Retrieve a GPO by its GUID."""
    try:
        initialize_com()
        gpm = win32com.client.Dispatch('GPMgmt.GPM')
        gpo = gpm.GetGPO(gpo_guid)
        return gpo
    except Exception as e:
        print(f"Failed to get GPO with GUID {gpo_guid}: {str(e)}")
        return None

def create_gpo(name, description):
    """Create a new GPO with the given name and description."""
    try:
        initialize_com()
        gpm = win32com.client.Dispatch('GPMgmt.GPM')
        gpo = gpm.CreateGPO(name, description)
        return gpo
    except Exception as e:
        print(f"Failed to create GPO: {str(e)}")
        return None

def update_gpo(gpo_guid, new_name, new_description):
    """Update an existing GPO with new name and description."""
    try:
        initialize_com()
        gpm = win32com.client.Dispatch('GPMgmt.GPM')
        gpo = get_gpo(gpo_guid)
        if gpo:
            gpo.Name = new_name
            gpo.Description = new_description
            gpo.Save()
            return gpo
        else:
            print(f"GPO with GUID {gpo_guid} not found.")
            return None
    except Exception as e:
        print(f"Failed to update GPO: {str(e)}")
        return None

def add_url_to_blacklist(url):
    """Add a URL to the blacklist and update GPO."""
    try:
        # Add URL to Django model
        Blacklist.objects.create(url=url)
        
        # Retrieve the GPO for updating
        gpo = get_gpo(settings.GPO_GUID)
        if gpo:
            # Add URL to GPO settings (replace with actual implementation)
            # Example: gpo.AddUrlToBlacklist(url)
            print(f"URL {url} added to GPO settings.")
            gpo.Save()
        else:
            print("GPO not found for updating.")
    except Exception as e:
        print(f"Failed to add URL to blacklist: {str(e)}")

def remove_url_from_blacklist(url):
    """Remove a URL from the blacklist and update GPO."""
    try:
        # Remove URL from Django model
        Blacklist.objects.filter(url=url).delete()
        
        # Retrieve the GPO for updating
        gpo = get_gpo(settings.GPO_GUID)
        if gpo:
            # Remove URL from GPO settings (replace with actual implementation)
            # Example: gpo.RemoveUrlFromBlacklist(url)
            print(f"URL {url} removed from GPO settings.")
            gpo.Save()
        else:
            print("GPO not found for updating.")
    except Exception as e:
        print(f"Failed to remove URL from blacklist: {str(e)}")

def convert_time(time_str):
    """Convert a time string to a datetime object."""
    from datetime import datetime
    return datetime.strptime(time_str, '%H:%M:%S')
# Example usage:

# def test_gpo_access():
#     try:
#         gpm = win32com.client.Dispatch("GPMgmt.GPM")
#         gpo_guid = "FC6FB68D-5D14-4BC1-8BF0-43018F119787"  # Replace with your actual GPO GUID
#         gpo = gpm.GetGPO(gpo_guid)
#         print("GPO retrieved successfully")
#     except Exception as e:
#         print(f"Error: {e}")
# def test_gpo_access():
#     gpo_guid = "{543594CD-606A-4BDE-860E-E3141ADA9D4B}"

#     pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
#     try:
#         logging.info("Creating GPM object...")
#         gpm = win32com.client.Dispatch("GPMgmt.GPM")
#         logging.info("GPM object created successfully.")
        
#         logging.info(f"Getting GPO with GUID: {gpo_guid}")
#         gpo = gpm.GetGPO(gpo_guid)
#         logging.info(f"GPO with GUID: {gpo_guid} retrieved successfully.")
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#     finally:
#         pythoncom.CoUninitialize()

# test_gpo_access()
# test_gpo_access()

# def explore_gpm_methods():
#     gpm = win32com.client.Dispatch("GPMgmt.GPM")
#     methods = dir(gpm)
#     print("Available methods and properties:")
#     for method in methods:
#         print(method)

# explore_gpm_methods()
#  Uninitialize COM
# gpm = win32com.client.Dispatch("GPMgmt.GPM")
# gpo_guid = "{YOUR_GPO_GUID}"
# gpo = gpm.GetGPO(gpo_guid)
# gpo_section = gpo.GetSection(2)
# logon_script_key = "Software\Policies\Microsoft\Windows\Scripts\Logon"
# gpo_section.SetRegistryValue(logon_script_key, "ScriptName", "path_to_your_script", winreg.REG_SZ)
# gpo_section.Save(True)



