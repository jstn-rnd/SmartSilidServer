from rest_framework import serializers
from server_app.models import UserLog, User, Computer, Section

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ('username', 'password', 'first_name', 'last_name', 'middle_initial')
        extra_kwargs = {
            'password': {'write_only': True}, 
        }

class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = ['user', 'computer', 'logonDateTime']  

class ComputerSerializer(serializers.ModelSerializer): 

    class Meta:
        model = Computer
        fields = ['computer_name', 'mac_address']  

class SectionSerializer(serializers.ModelSerializer): 

    class Meta : 
        model = Section
        fields = ['name']

#class UserUsernameSerializer()