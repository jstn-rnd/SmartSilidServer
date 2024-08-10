from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    middle_initial = models.CharField(default=" ", max_length=255)
    type = models.CharField(default=" ", max_length=255)
    section = models.CharField(default=" ", max_length=255)

class UserLog(models.Model): 
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserLogs')
    dateTime = models.DateTimeField()

class ComputerLogs(models.Model):
    id = models.AutoField(primary_key=True)
    computerName = models.CharField(max_length=255)
    dateTime = models.DateTimeField()

class Test(models.Model):
    RFID = models.CharField(max_length=30, unique=True)
    approved = models.IntegerField(default=0)  # Using IntegerField for 0 and 1 values

class MacAddress(models.Model):
    mac_address = models.CharField(max_length=50)

class Whitelist(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class Blacklist(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class StudentMAC(models.Model):
    id = models.AutoField(primary_key=True)
    computer_name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=50)

    def __str__(self):
        return self.computer_name
