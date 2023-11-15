from django import forms
from .models import User, team_members

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = team_members
        fields=['teammember1_name','teammember1_email','role1','teammember2_name','teammember2_email','role2','teammember3_name','teammember3_email','role3']