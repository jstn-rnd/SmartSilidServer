from rest_framework import serializers
from server_app.models import UserLog, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ('username', 'password', 'first_name', 'last_name', 'middle_initial')
        extra_kwargs = {
            'password': {'write_only': True}, 
        }

class UserLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  

    class Meta:
        model = UserLog
        fields = ['username', 'dateTime']  

    def validate(self, data):
        username = data.get('username')
        if not username:
            raise serializers.ValidationError({"username": "This field is required."})
        
        try:
            user = User.objects.get(username=username)
            print("Trueeeeeee")
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "User with this username does not exist."})
        
        data['user'] = user
        return data

    def create(self, validated_data):
        validated_data.pop('username')
        return super().create(validated_data)
