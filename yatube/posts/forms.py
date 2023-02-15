from django.forms import ModelForm
from django import forms
from django.contrib.auth import get_user_model

from .models import Post

User = get_user_model()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image') 
        
# class PostForm(ModelForm):
#     class Meta:
#         model = Post
#         fields = ("text", "group")

