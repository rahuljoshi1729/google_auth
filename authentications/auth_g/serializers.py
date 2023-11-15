from rest_framework import serializers
from .models import User, team_members

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = team_members
        fields = '__all__'
