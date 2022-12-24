from rest_framework import serializers
from user_management.models import User
import xmlrpc.client

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['username', 'db', 'url','key']
        
    
    def validate(self, attrs):
        db = attrs.get('db')
        url = attrs.get('url')
        username = attrs.get('username')
        password = attrs.get('key')
        print(db,"====db===")
        print(url,"====url===")
        print(username,"====username===")
        print(password,"====password===")
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        is_auth = common.authenticate(db, username, password, {})
        if not is_auth:
            raise serializers.ValidationError("Sorry Register Failed")
        return attrs

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
  username = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['username','key','db','url']