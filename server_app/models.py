from django.db import models


class UserLogs(models.Model): 
    id = models.AutoField(primary_key=True)
    userName = models.CharField(default = " ", max_length=255)
    dateTime = models.DateTimeField()

class ComputerLogs(models.Model): 
    id = models.AutoField(primary_key=True)
    computerName = models.CharField(max_length = 255)
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