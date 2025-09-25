from django.forms import ModelForm
from .models import Room, Profile
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']
        # for '__all__' includes all fields in the Room Model, 
        # subsequently want to hide fields like user that should be auto generated

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_img"]