from django.contrib import admin
from .models import User, UserLog, Scan, Computer, Section, Student, RFID, BlockedURL, Schedule, RfidLogs

admin.site.register(Student)
admin.site.register(RFID)
admin.site.register(User)
admin.site.register(UserLog)
admin.site.register(Computer)
admin.site.register(Section)
admin.site.register(BlockedURL)
admin.site.register(Schedule)
admin.site.register(RfidLogs)
admin.site.register(Scan)