from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date

class User(AbstractUser):
    middle_initial = models.CharField(default= " ", max_length=1)
    type = models.CharField(default=" ", max_length=20)
    hasWindows = models.IntegerField(default=0)

class Section(models.Model): 
    id = models.AutoField(primary_key=True)
    name = models.CharField(default=" ", max_length=255)
    
class Student(models.Model):
    first_name = models.CharField(default=" ", max_length=20)
    middle_initial = models.CharField(default=" ", max_length=1)
    last_name = models.CharField(default=" ", max_length=20)
    username = models.CharField(default=" ", max_length=20)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='Users', null = True)

    def __str__(self):
        return self.username
    
# 0 is false, 1 is true
class Computer(models.Model):
    id = models.AutoField(primary_key=True)
    computer_name = models.CharField(max_length=255, default= " ")
    mac_address = models.CharField(max_length=50, default = " ")
    status = models.IntegerField(default=0)
    is_admin = models.IntegerField(default=0)

    def __str__(self):
        return self.computer_name

class Semester(models.Model): 
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, blank=True, max_length=255)
    isActive = models.BooleanField(default=False)

class UserLog(models.Model): 
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255, null= True, blank= True)
    computer = models.CharField(max_length=255, null= True, blank= True)
    section = models.CharField(max_length=255, null= True, blank= True)
    date = models.DateField()
    logonTime = models.TimeField(null = True, blank = True)
    logoffTime = models.TimeField(null = True, blank = True)

class RFID(models.Model):
    rfid = models.CharField(max_length=30, unique=True)
    approved = models.IntegerField(default=0)  # Using IntegerField for 0 and 1 values

    def __str__(self):
        return self.rfid

from django.utils.translation import gettext_lazy as _

class Schedule(models.Model):

    WEEKDAYS = [
        ('M', 'Monday'),
        ('T', 'Tuesday'),
        ('W', 'Wednesday'),
        ('R', 'Thursday'),
        ('F', 'Friday'),
        ('S', 'Saturday'),
        ('U', 'Sunday'),
    ]
    
    subject = models.CharField(max_length=255)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    weekdays = models.CharField(max_length=1, choices=WEEKDAYS)
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="Schedule")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="Schedule")

    def __str__(self):
        return f"{self.subject} ({self.start_time} - {self.end_time})"

class BlockedURL(models.Model):
    url = models.URLField(unique=True)
    
    def __str__(self):
        return self.url

class ClassInstance(models.Model): 
    schedule = models.ForeignKey(Schedule, on_delete = models.CASCADE)
    date = models.DateField(default = datetime.today().date())

class Attendance(models.Model): 
    class_instance = models.ForeignKey(ClassInstance, on_delete=models.CASCADE)
    fullname = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(null=True, blank=True, max_length=255)
    scan_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))

class RfidLogs(models.Model): 
    user = models.CharField(null=True, blank=True, max_length=255)
    date = models.DateField(default=datetime.today().date())
    scan_time = models.TimeField(default=datetime.now().strftime("%H:%M:%S"))
    type = models.CharField(null=True, blank=True, max_length=255, choices=[("student", "student"), ("faculty", "faculty")])

class Scan(models.Model): 
    id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="Scans")
    student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL, blank=True, related_name="Scans")
    computer = models.ForeignKey(Computer, null=True, on_delete=models.SET_NULL, blank=True, related_name="Scans")
    rfid = models.ForeignKey(RFID, null=True, blank=True, on_delete=models.SET_NULL, related_name="scans")
    
    def delete(self, *args, **kwargs):
        # Delete the parent before deleting the child
        if self.rfid:
            self.rfid.delete()
        
        if self.student: 
            self.student.delete()
        super().delete(*args, **kwargs)

