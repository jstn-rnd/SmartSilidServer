from django.contrib import admin
from .models import Test, MacAddress, User, UserLog, Computer, Section

admin.site.register(Test)
admin.site.register(MacAddress)
admin.site.register(User)
admin.site.register(UserLog)
admin.site.register(Computer)
admin.site.register(Section)
