import pyad
from pyad import *
import pythoncom
from pyad.adquery import ADQuery

pythoncom.CoInitialize()  # Ensure CoInitialize is called before any COM object is used
from pyad import * 
AD_SERVER = "SERVER.justine-server.com"
AD_USER = "ewan"
AD_PASSWORD = "Nitrosense55"


def get_ad_connection():
    try:
        pythoncom.CoInitialize()  # Initialize the COM library
        pyad.set_defaults(ldap_server=AD_SERVER, username=AD_USER, password=AD_PASSWORD)
        return True
    except Exception as e:
        print(f"Failed to connect to AD: {str(e)}")
        return False