from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class User(AbstractUser):
    middle_initial = models.CharField(default=" ", max_length=255)
    type = models.CharField(default=" ", max_length=255)
    section = models.CharField(default=" ", max_length=255)

class Computer(models.Model):
    id = models.AutoField(primary_key=True)
    computer_name = models.CharField(max_length=255, default= " ")
    mac_address = models.CharField(max_length=50, default = " ")

    def __str__(self):
        return self.computer_name

class UserLog(models.Model): 
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserLogs')
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name='UserLogs', default = 0)
    dateTime = models.DateTimeField()

class ComputerLogs(models.Model):
    id = models.AutoField(primary_key=True)
    computerName = models.CharField(max_length=255)
    dateTime = models.DateTimeField()

class Test(models.Model):
    RFID = models.CharField(max_length=30, unique=True)
    approved = models.IntegerField(default=0)  # Using IntegerField for 0 and 1 values

    def __str__(self):
        return self.RFID
    
class MacAddress(models.Model):
    mac_address = models.CharField(max_length=50)



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
    start_time = models.TimeField()
    end_time = models.TimeField()
    weekdays = models.CharField(max_length=1, choices=WEEKDAYS)
    rfids = models.ManyToManyField('Test', blank=True)
    
    def __str__(self):
        return f"{self.subject} ({self.start_time} - {self.end_time})"






class Whitelist(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class Blacklist(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

