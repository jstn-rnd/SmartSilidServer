from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Replace with your actual user model
        fields = ('username', 'password', 'first_name', 'last_name', 'middle_initial')
        extra_kwargs = {
            'password': {'write_only': True},  # Hide password in response
        }