from django.contrib import admin
from .models import Test, MacAddress, User, UserLog, StudentMAC

admin.site.register(Test)
admin.site.register(MacAddress)
admin.site.register(User)
admin.site.register(UserLog)
admin.site.register(StudentMAC)