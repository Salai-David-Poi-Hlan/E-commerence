from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,style={'input_type':'password'})


    class Meta:
        model=User
        fields=['username','email','password']
        extra_kwargs={'email':{'required':True,'allow_blank':False}}



    def validate_username(self,value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is taken")
        return value

    

    def validate_email(self,value):
        value=value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists')
        return value
    

    def validate(self,attrs):
        candidate=User(username=attrs['username'],email=attrs['email'])
        try:
            validate_password(attrs['password'],candidate)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})
        return attrs
    

    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
