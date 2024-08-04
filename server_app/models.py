from django.db import models


class UserLogs(models.Model): 
    id = models.AutoField(primary_key=True)
    userName = models.CharField(default = " ", max_length=255)
    dateTime = models.DateTimeField()

class ComputerLogs(models.Model): 
    id = models.AutoField(primary_key=True)
    computerName = models.CharField(max_length = 255)
    dateTime = models.DateTimeField()






class Whitelist(models.Model):
    url = models.URLField(unique=True)

class Blacklist(models.Model):
    url = models.URLField(unique=True)